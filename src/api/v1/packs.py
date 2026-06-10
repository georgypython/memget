from fastapi import APIRouter, Depends, Body, HTTPException, status
from pydantic import Field

from src.dependencies.services import get_memory_service
from src.services.memory import MemoryService



router = APIRouter()


@router.post("/")
async def create_pack(
    name: str = Body(min_length=1, max_length=200),
    service: MemoryService = Depends(get_memory_service),
):
    try:
        return await service.create_pack(name)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
