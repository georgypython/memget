from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from src.schemas.packs import PackSchema


class DocumentSchema(BaseModel):
    id: UUID
    name: str
    pack_id: UUID
    created_at: datetime
    pack: PackSchema | None = None
