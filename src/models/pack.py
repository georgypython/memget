from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, func, Table, ForeignKey, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .chat import ChatOrm
    from .documents import DocumentOrm


pack_chats = Table(
    "pack_chats",
    Base.metadata,
    Column("pack_id", ForeignKey("packs.id", ondelete="CASCADE"), primary_key=True),
    Column("chat_id", ForeignKey("chats.id", ondelete="CASCADE"), primary_key=True),
)


class PackOrm(Base):
    __tablename__ = "documents"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    
    documents: Mapped["DocumentOrm | None"] = relationship(
            "documents.id", back_populates="pack", 
    )
    chats: Mapped[list["ChatOrm | None"]] = relationship(
        "chats.id", back_populates="packs", secondary=pack_chats
    )


