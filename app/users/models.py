from datetime import datetime, timedelta

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config import settings
from app.core.database.base import Base


class User(Base):
    """
    Represents a user.

    Attributes:
        name: (str),
        patronymic: (str),
        surname: (str),
        email: (str),
        password: (str),
        date_of_birth: (str),
        is_email_verified: (bool),
    """

    __tablename__ = "users"
    name: Mapped[str] = mapped_column(String(200))
    patronymic: Mapped[str] = mapped_column(String(200))
    surname: Mapped[str] = mapped_column(String(200))
    email: Mapped[str] = mapped_column(String(200))
    password: Mapped[str] = mapped_column(String(200))
    date_of_birth: Mapped[str] = mapped_column(String(200))
    is_email_verified: Mapped[bool] = mapped_column(Boolean(), default=False)


class VerificationCode(Base):
    """
    Provides codes for verifying the user's mail.
    """

    __tablename__ = "verification_codes"

    user_id: Mapped[int] = mapped_column(
        BigInteger(), ForeignKey("users.id"), nullable=False
    )
    user = relationship(
        "User",
        foreign_keys=[user_id],
    )
    code: Mapped[str] = mapped_column(String(10))
    expired_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now()
        + timedelta(minutes=settings.app.VERIFICATION_CODE_EXPIRE_MINUTES),
    )
