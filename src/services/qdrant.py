from qdrant_client import AsyncQdrantClient

from src.core.config import settings

qdrant = AsyncQdrantClient(
    host=settings.qdrant.host,
    port=settings.qdrant.port,
    api_key=settings.security.api_key,
    https=False,
)
