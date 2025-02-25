from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from .models import User


class UserCreate(BaseModel):
    name: str
    patronymic: str
    surname: str
    date_of_birth: str
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    patronymic: str
    surname: str
    email: str
    date_of_birth: str
    is_email_verified: bool

    model_config = {"from_attributes": True}


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
