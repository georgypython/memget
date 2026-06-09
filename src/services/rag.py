from qdrant_client import QdrantClient

from src.core.config import settings


class QdrantService:
    def __init__(self):
        self.client = QdrantClient(
            host=settings.qdrant.host,
            port=settings.qdrant.port,
            api_key=settings.qdrant.api_key,
        )

    

qdrant = QdrantService()
