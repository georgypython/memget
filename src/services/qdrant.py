from qdrant_client import QdrantClient

from src.core.config import settings


class QdrantService:
    def __init__(self):
        self.client = QdrantClient(
            host=settings.qdrant.host,
            port=settings.qdrant.port,
            api_key=settings.security.api_key,
        )
    
    async def create_pack(self, name: str):
        pass
    

qdrant_service = QdrantService()
