from fastapi import APIRouter

from src.core.config import settings

from src.api.v1 import packs

router = APIRouter()


router.include_router(packs.router, prefix="/packs")
