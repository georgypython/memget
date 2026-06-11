from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.dependencies.session import get_session
from src.services.memory import MemoryService
from src.services.qdrant import qdrant
from src.services.http import http_client
from src.core.config import settings


async def get_memory_service(
    session: AsyncSession = Depends(get_session),
) -> MemoryService:
    return MemoryService(
        qdrant,
        session,
        http_client=http_client,
        embed_url=settings.models.embed_url,
    )
