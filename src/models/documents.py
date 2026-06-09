from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, func, Table, ForeignKey, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


if TYPE_CHECKING:
    from .chat import ChatOrm
    from .pack import PackOrm


chat_docs = Table(
    "chat_docs",
    Base.metadata,
    Column("chat_id", ForeignKey("chats.id", ondelete="CASCADE"), primary_key=True),
    Column("documents_id", ForeignKey("documents.id", ondelete="CASCADE"), primary_key=True),
)


class DocumentOrm(Base):
    __tablename__ = "documents"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    
    pack: Mapped["PackOrm"] = relationship(
            "packs.id", back_populates="documents"
    )
    chats: Mapped[list["ChatOrm | None"]] = relationship(
            "chats.id", back_populates="documents", secondary=chat_docs
    )


