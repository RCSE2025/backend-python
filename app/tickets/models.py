from datetime import datetime, timedelta

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, String, func, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config import settings
from app.core.database.base import Base


class Ticket(Base):
    __tablename__ = "tickets"
    id: Mapped[int] = mapped_column(
        Integer(),
        primary_key=True,
        autoincrement=False,
    )
    title: Mapped[str] = mapped_column(String(256))
    status: Mapped[str] = mapped_column(String(256))
    username: Mapped[str] = mapped_column(String(256))
