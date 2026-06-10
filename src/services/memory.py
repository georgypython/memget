from sqlalchemy.ext.asyncio import AsyncSession
from qdrant_client import AsyncQdrantClient, models
from qdrant_client.http.exceptions import UnexpectedResponse

from src.models.pack import PackOrm
from src.schemas.packs import PackSchema
from src.core.logger_setup import logger


class MemoryService:
    def __init__(self, qdrant: AsyncQdrantClient, session: AsyncSession) -> None:
        self.qdrant = qdrant
        self.session = session

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
