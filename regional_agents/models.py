import enum
from datetime import datetime
from typing import Optional

import ormar

from database import base_ormar_config
from users.models import User


class RegionalAgents(ormar.Model):
    ormar_config = base_ormar_config.copy(tablename="regional_agents")

    id: int = ormar.Integer(primary_key=True)
    title: str = ormar.String(max_length=200)
    description: Optional[str] = ormar.String(max_length=1000, default="")
    federal_subject: str = ormar.String(max_length=200)
    address: str = ormar.String(max_length=200, default="")
    telegram: Optional[str] = ormar.String(max_length=200, default="")
    vk: Optional[str] = ormar.String(max_length=200, default="")
    email: Optional[str] = ormar.String(max_length=200, default="")
    phone_number: Optional[str] = ormar.String(max_length=200, default="")
    user_id: Optional[User] = ormar.ForeignKey(User, ondelete="SET NULL", nullable=True)
    fio: Optional[str] = ormar.String(max_length=200, default="")
    iso_code: str = ormar.String(max_length=200, nullable=True)
    region_emblem_url: str = ormar.String(max_length=200, nullable=True)

    created_at: str = ormar.String(
        max_length=200, default=lambda: datetime.now().isoformat() + "Z"
    )
    updated_at: str = ormar.String(
        max_length=200, default=lambda: datetime.now().isoformat() + "Z"
    )
