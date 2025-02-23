import enum
from datetime import datetime, timedelta, timezone
from typing import Optional

import ormar

from config import VERIFICATION_CODE_EXPIRE_MINUTES
from database import base_ormar_config


class UserRoleEnum(enum.Enum):
    SPORTSMAN = "SPORTSMAN"
    AGENT = "AGENT"
    ROOT = "ROOT"


class AgentStatusEnum(enum.Enum):
    WAITING = "WAITING"
    APPROVED = "APPROVED"
    DECLINED = "DECLINED"


class User(ormar.Model):
    ormar_config = base_ormar_config.copy(tablename="users")

    id: int = ormar.Integer(primary_key=True)
    name: str = ormar.String(max_length=200)
    patronymic: str = ormar.String(max_length=200)
    surname: str = ormar.String(max_length=200)
    email: str = ormar.String(max_length=200)
    password: str = ormar.String(max_length=200)
    date_of_birth: str = ormar.String(max_length=200)
    role: UserRoleEnum = ormar.String(max_length=200)
    is_email_verified: bool = ormar.Boolean(default=False)
    status: AgentStatusEnum = ormar.String(
        max_length=200, default=AgentStatusEnum.WAITING.value
    )

    created_at: str = ormar.String(
        max_length=200, default=lambda: datetime.now().isoformat() + "Z"
    )
    updated_at: str = ormar.String(
        max_length=200, default=lambda: datetime.now().isoformat() + "Z"
    )


class VerificationCode(ormar.Model):
    ormar_config = base_ormar_config.copy(tablename="verification_codes")

    id: int = ormar.Integer(primary_key=True)
    user: User = ormar.ForeignKey(User, ondelete="CASCADE")
    code: str = ormar.String(max_length=10)
    send_at: datetime = ormar.DateTime(default=datetime.now, timezone=True)
    expired_at: datetime = ormar.DateTime(
        default=lambda: datetime.now(timezone.utc)
        + timedelta(minutes=VERIFICATION_CODE_EXPIRE_MINUTES),
        timezone=True,
    )
