from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.dependencies.session import get_session
from src.services.memory import MemoryService
from src.services.qdrant import qdrant


async def get_memory_service(session: AsyncSession = Depends(get_session)) -> MemoryService:
    return MemoryService(qdrant, session)
