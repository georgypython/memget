from typing import TYPE_CHECKING
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .message import MessageOrm
    from .documents import DocumentOrm


class ChatOrm(Base):
    __tablename__ = "chats"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(nullable=False, unique=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    
    messages: Mapped[list["MessageOrm | None"]] = relationship(
            "messsages.id", back_populates="chat", cascade="all, delete-orphan"
    )
    documents: Mapped[list["DocumentOrm | None"]] = relationship("documents.id", back_populates="chats")

