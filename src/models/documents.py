from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, func 
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from src.models.chat import chat_docs

if TYPE_CHECKING:
    from .chat import ChatOrm
    from .pack import PackOrm


class DocumentOrm(Base):
    __tablename__ = "documents"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    pack_id: Mapped[UUID] = mapped_column(ForeignKey("packs.id"), nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    
    pack: Mapped["PackOrm"] = relationship(
            "PackOrm", back_populates="documents"
    )
    chats: Mapped[list["ChatOrm | None"]] = relationship(
            "ChatOrm", back_populates="documents", secondary=chat_docs
    )


