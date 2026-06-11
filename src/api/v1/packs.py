from uuid import UUID
from fastapi import APIRouter, Depends, Body, File, HTTPException, UploadFile, status
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


@router.post("/{id}/documents")
async def add_document_to_pack_by_id(
    id: UUID,
    document: UploadFile = File(...),
    service: MemoryService = Depends(get_memory_service)
):
    await service.upload_document_to_pack(
        id, document.file, document.filename, document.content_type
    )

