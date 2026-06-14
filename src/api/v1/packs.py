from uuid import UUID
from fastapi import APIRouter, Depends, Body, File, HTTPException, UploadFile, status

from src.dependencies.services import get_memory_service
from src.schemas.document import DocumentSchema
from src.schemas.packs import PackSchema
from src.services.memory import MemoryService

router = APIRouter()


@router.post("/", response_model=PackSchema)
async def create_pack(
    name: str = Body(min_length=1, max_length=200),
    service: MemoryService = Depends(get_memory_service),
):
    try:
        return await service.create_pack(name)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@router.get("/", response_model=list[PackSchema])
async def get_packs_list(
    service: MemoryService = Depends(get_memory_service)
):
    return await service.get_packs()


@router.get("/{id}", response_model=PackSchema)
async def get_pack_by_id(
    id: UUID,
    service: MemoryService = Depends(get_memory_service),
):
    try:
        return await service.get_pack(id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{id}/documents", response_model=DocumentSchema)
async def add_document_to_pack_by_id(
    id: UUID,
    document: UploadFile = File(...),
    service: MemoryService = Depends(get_memory_service),
):
    try:
        return await service.upload_document_to_pack(
            id, document.file, document.filename, document.content_type
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@router.get("/{id}/documents")
async def get_pack_documents_list(
    id: UUID,
    service: MemoryService = Depends(get_memory_service),
):
    return await service.get_pack_documents_list(id) 

@router.get("/{id}/exists")
async def check_pack_exists(
    id: UUID, 
    service: MemoryService = Depends(get_memory_service),
):
    status = await service.is_pack_collection_exists(id)
    return {"status": status}


@router.get("/{id}/question")
async def send_pack_question(
    id: UUID,
    question: str,
    service: MemoryService = Depends(get_memory_service),
):
    return await service.send_pack_question(id, question)
