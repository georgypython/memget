from src.services.qdrant import QdrantService, qdrant_service


async def get_qdrant_service() -> QdrantService:
    return qdrant_service
