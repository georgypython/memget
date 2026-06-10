from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field



class PackSchema(BaseModel):
    id: UUID
    name: str = Field(min_length=1, max_length=200)
    created_at: datetime
