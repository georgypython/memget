from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, func 
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from src.models.chat import pack_chats

if TYPE_CHECKING:
    from .chat import ChatOrm
    from .documents import DocumentOrm


class PackOrm(Base):
    __tablename__ = "packs"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    
    documents: Mapped["DocumentOrm | None"] = relationship(
            "DocumentOrm", back_populates="pack", 
    )
    chats: Mapped[list["ChatOrm | None"]] = relationship(
        "ChatOrm", back_populates="packs", secondary=pack_chats
    )


