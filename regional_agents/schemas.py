from typing import Optional

from pydantic import BaseModel

from users.schemas import UserResponse

from .models import RegionalAgents


class RegionalAgentCreate(BaseModel):
    title: str = None
    description: Optional[str] = None
    federal_subject: str
    address: Optional[str] = None
    telegram: Optional[str] = None
    vk: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    fio: Optional[str] = None


class RegionalAgentResponse(
    RegionalAgents.get_pydantic(exclude={"created_at", "updated_at", "user_id"})
):
    pass


class RegionalAgentResponseWithUser(
    RegionalAgents.get_pydantic(exclude={"created_at", "updated_at", "user_id"})
):
    user_id: UserResponse | None = None


class RegionalAgentUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    address: str | None = None
    telegram: str | None = None
    vk: str | None = None
    email: str | None = None
    phone_number: str | None = None
    fio: str | None = None


class FilterRegionalAgent(BaseModel):
    limit: Optional[int] = 20
    offset: Optional[int] = 0

    title: Optional[str] = None
    federal_subject: Optional[str] = None
    fio: Optional[str] = None
