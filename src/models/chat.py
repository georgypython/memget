from typing import TYPE_CHECKING
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, func, Table, Column, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .message import MessageOrm
    from .documents import DocumentOrm
    from .pack import PackOrm


pack_chats = Table(
    "pack_chats",
    Base.metadata,
    Column("pack_id", ForeignKey("packs.id", ondelete="CASCADE"), primary_key=True),
    Column("chat_id", ForeignKey("chats.id", ondelete="CASCADE"), primary_key=True),
)

chat_docs = Table(
    "chat_docs",
    Base.metadata,
    Column("chat_id", ForeignKey("chats.id", ondelete="CASCADE"), primary_key=True),
    Column("documents_id", ForeignKey("documents.id", ondelete="CASCADE"), primary_key=True),
)


class ChatOrm(Base):
    __tablename__ = "chats"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(nullable=False, unique=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    
    messages: Mapped[list["MessageOrm | None"]] = relationship(
            "MessageOrm", back_populates="chat", cascade="all, delete-orphan"
    )
    documents: Mapped[list["DocumentOrm | None"]] = relationship(
        "DocumentOrm", back_populates="chats", secondary=chat_docs
    )
    packs: Mapped[list["PackOrm | None"]] = relationship(
        "PackOrm", back_populates="chats", secondary=pack_chats
    )
