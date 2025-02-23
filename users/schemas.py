from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from regional_agents.models import RegionalAgents

from .models import User, UserRoleEnum


class UserCreate(BaseModel):
    name: str
    patronymic: str
    surname: str
    date_of_birth: str
    role: UserRoleEnum
    email: str
    password: str


class UserResponse(
    User.get_pydantic(
        exclude={
            "password",
            "created_at",
            "updated_at",
            "verificationcodes",
            "regionalagentss",
        }
    )
):
    pass


class Token(BaseModel):
    access_token: str
    token_type: str


class RefreshAccessToken(BaseModel):
    refresh_token: str
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: int | None = None


class UserUpdate(BaseModel):
    email: str | None = None
    name: str | None = None
    patronymic: str | None = None
    surname: str | None = None
    date_of_birth: str | None = None
