from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, String, func, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config import settings
from app.core.database.base import Base


class Comment(Base):
    __tablename__ = "comments"
    
    text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id", ondelete="CASCADE"))
    username: Mapped[str] = mapped_column(String(256))
    
    # Relationship
    ticket: Mapped["Ticket"] = relationship("Ticket", back_populates="comments")


class Ticket(Base):
    __tablename__ = "tickets"
    
    title: Mapped[str] = mapped_column(String(256))
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(256))
    username: Mapped[str] = mapped_column(String(256))
    
    # Relationship
    comments: Mapped[list[Comment]] = relationship(
        "Comment",
        back_populates="ticket",
        cascade="all, delete-orphan"
    )
