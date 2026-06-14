from typing import BinaryIO
from io import BytesIO
from uuid import UUID, uuid4

from docling.document_converter import DocumentConverter
from docling_core.types.doc.document import DoclingDocument
from docling_core.transforms.chunker.hybrid_chunker import HybridChunker
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from qdrant_client import AsyncQdrantClient, models
from qdrant_client.http.exceptions import UnexpectedResponse
from docling.datamodel.base_models import InputFormat, DocumentStream
from docling_core.transforms.chunker.tokenizer.openai import OpenAITokenizer
import tiktoken
from httpx import AsyncClient

from src.models import PackOrm, DocumentOrm
from src.schemas.document import DocumentSchema
from src.schemas.packs import PackSchema
from src.core.logger_setup import logger


class MemoryService:
    def __init__(
        self,
        qdrant: AsyncQdrantClient,
        session: AsyncSession,
        http_client: AsyncClient,
        embed_url: str,
    ) -> None:
        self.qdrant = qdrant
        self.session = session
        self.http_client = http_client
        self.embed_url = embed_url
        self._allowed_formats = {
            "application/pdf": InputFormat.PDF,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": InputFormat.DOCX,
            "application/msword": InputFormat.DOCX,
            "application/vnd.openxmlformats-officedocument.presentationml.presentation": InputFormat.PPTX,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": InputFormat.XLSX,
            "text/markdown": InputFormat.MD,
            "text/plain": InputFormat.MD,
            "text/html": InputFormat.HTML,
            "text/csv": InputFormat.CSV,
            "application/epub+zip": InputFormat.EPUB,
            "image/jpeg": InputFormat.IMAGE,
            "image/png": InputFormat.IMAGE,
            "message/rfc822": InputFormat.EMAIL,
        }
        self.converter = DocumentConverter()
        self.chunker = HybridChunker(
            tokenizer=OpenAITokenizer(
                tokenizer=tiktoken.get_encoding("cl100k_base"), max_tokens=800
            )
        )

    async def create_pack(self, name: str):
        try:
            await self.qdrant.create_collection(
                collection_name=name,
                vectors_config=models.VectorParams(
                    size=768, distance=models.Distance.COSINE
                ),
            )
        except UnexpectedResponse as e:
            logger.warning(e)
            raise ValueError(f"Pack with name: {name} already exists")

        pack = PackOrm(name=name)
        self.session.add(pack)
        await self.session.flush()
        await self.session.commit()

        return pack.from_orm_to_schema()

    def convert_document_for_chunking(
        self, file: BinaryIO, file_name: str, content_type: str
    ) -> DoclingDocument:
        content = file.read()
        stream = BytesIO(content)

        input_format = self._allowed_formats.get(content_type)
        if not input_format:
            raise ValueError("Invalid content type")

        doc_stream = DocumentStream(name=file_name, stream=stream)
        return self.converter.convert(doc_stream).document

    async def get_text_vector(self, text: str, search_query: bool = False):
        if search_query:
            prompt = f"search_query: {text}"
        else:
            prompt = f"search_document: {text}"

        resp = await self.http_client.post(
            self.embed_url,
            timeout=30,
            json={"model": "nomic-embed-text", "prompt": prompt},
        )
        return resp.json()["embedding"]

    async def save_vectors_to_collection(
        self, name: str, vectors: list[list[float]], texts: list[str]
    ) -> None:
        points = []
        for vector, text in zip(vectors, texts):
            payload = {"text": text}

            point = models.PointStruct(id=uuid4(), vector=vector, payload=payload)
            points.append(point)

        await self.qdrant.upsert(name, points)

    async def upload_document_to_pack(
        self,
        pack_id: UUID,
        file: BinaryIO,
        file_name: str | None,
        content_type: str | None,
    ) -> DocumentSchema:
        if not content_type:
            raise ValueError("Unknown content_type")
        pack = await self.session.get(PackOrm, pack_id)
        if not pack:
            raise ValueError("Pack not found")
        try:
            doc_id = uuid4()
            document = DocumentOrm(name=file_name or str(doc_id), pack_id=pack.id)
            converted_doc = self.convert_document_for_chunking(
                file, document.name, content_type
            )
            chunks = list(self.chunker.chunk(converted_doc))
            texts = [c.text for c in chunks]

            vectors = [await self.get_text_vector(text, False) for text in texts]

            await self.save_vectors_to_collection(
                name=pack.name, vectors=vectors, texts=texts
            )

            self.session.add(document)
            await self.session.commit()
            return DocumentSchema(
                id=document.id, 
                name=document.name, 
                pack_id=pack.id, 
                created_at=document.created_at
            ) 
        except Exception as e:
            logger.error(e)
            await self.session.rollback()
            raise

    async def get_pack(self, id: UUID) -> PackSchema:
        pack = await self.session.get(PackOrm, id)
        if not pack:
            raise ValueError(f"Pack whith id: {id} not found")
        return pack.from_orm_to_schema()

    async def get_packs(self) -> list[PackSchema]:
        stmt = select(PackOrm)
        result = await self.session.execute(stmt)
        packs_orm = result.scalars().all()

        if not packs_orm:
            return []
        return [orm.from_orm_to_schema() for orm in packs_orm]

    
    async def is_pack_collection_exists(self, id: UUID) -> bool:
        pack = await self.session.get(PackOrm, id)
        if not pack:
            raise ValueError("Pack not found")

        return await self.qdrant.collection_exists(pack.name)

    async def get_pack_documents_list(self, id: UUID) -> list[DocumentSchema]:
        stmt = select(DocumentOrm).where(DocumentOrm.pack_id == id)
        result = await self.session.execute(stmt)
        docs_orm = result.scalars().all()

        if not docs_orm:
            return []
        
        return [orm.from_orm_to_schema() for orm in docs_orm]
    
    async def send_pack_question(self, id: UUID, question: str):
        pack = await self.session.get(PackOrm, id)
        if not pack:
            raise ValueError("Pack not found")

        if not self.is_pack_collection_exists(id):
            raise ValueError("Pack collection doesnt exists")

        vector = await self.get_text_vector(question, True)

        answer = await self.qdrant.query_points(
            collection_name=pack.name, query=vector, limit=50, with_payload=True
        )
        resp: list[tuple[str, float]] = []

        for p in answer.points:
            payload = p.payload or {}
            text: str = payload.get("text", "")
            clean_text = text.replace('\n', ' ')
            resp.append((clean_text, p.score))
        return resp
