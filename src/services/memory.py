from typing import BinaryIO
from io import BytesIO
from uuid import UUID

from docling.document_converter import DocumentConverter
from docling_core.types.doc.document import DoclingDocument
from docling_core.transforms.chunker.hybrid_chunker import HybridChunker
from sqlalchemy.ext.asyncio import AsyncSession
from qdrant_client import AsyncQdrantClient, models
from qdrant_client.http.exceptions import UnexpectedResponse
from docling.datamodel.base_models import InputFormat, DocumentStream
from docling_core.transforms.chunker.tokenizer.openai import OpenAITokenizer
import tiktoken


from src.models.pack import PackOrm
from src.schemas.packs import PackSchema
from src.core.logger_setup import logger


class MemoryService:
    def __init__(
        self, 
        qdrant: AsyncQdrantClient, 
        session: AsyncSession,
        embed_model: str,
        embed_path: str, 
    ) -> None:
        self.qdrant = qdrant
        self.session = session
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
        try :
            await self.qdrant.create_collection(
                collection_name=name, vectors_config=models.VectorParams(
                    size=768, distance=models.Distance.COSINE
                    )    
            )
        except UnexpectedResponse as e:
            logger.warning(e)
            raise ValueError(f"Pack with name: {name} already exists")
    
        pack = PackOrm(name=name)
        self.session.add(pack)
        await self.session.flush()
        await self.session.commit()

        return PackSchema(
            id=pack.id, name=pack.name, created_at=pack.created_at
        )

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

    async def upload_document_to_pack(
        self, pack_id: UUID, file: BinaryIO, file_name: str | None, content_type: str | None
    ):
        if not content_type:
            raise ValueError("Unknown content_type")
        pack = await self.session.get(PackOrm, pack_id)
        if not pack:
            raise ValueError("Pack not found")

        converted_doc = self.convert_document_for_chunking(file, file_name or "", content_type)
        chunks = list(self.chunker.chunk(converted_doc))
        texts = [c.text for c in chunks]

        
