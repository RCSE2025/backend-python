from typing import Annotated, List

from fastapi import APIRouter, Depends, Form, Header, Query

from app.users.models import User
from app.users.schemas import RefreshAccessToken, UserCreate, UserResponse, UserUpdate
from app.users.services import UserService

users_router = APIRouter(tags=["user"], prefix="/user")


@users_router.post("/register")
async def register(user_create: UserCreate) -> RefreshAccessToken:
    _, tokens = await UserService().create(user_create)

    return tokens


@users_router.post("/refresh")
async def refresh_token_route(
    refresh_token: Annotated[str, Form()]
) -> RefreshAccessToken:
    return await UserService().refresh_token(refresh_token)


@users_router.post("/token")
async def login_for_access_token(
    username: Annotated[str, Form()], password: Annotated[str, Form()]
) -> RefreshAccessToken:
    return await UserService().login_user(username, password)


@users_router.get("/self")
async def get_self(
    current_user: Annotated[User, Depends(UserService().get_current_user)],
) -> UserResponse:
    return UserResponse.model_validate(current_user)


@users_router.delete("")
async def delete_user(
    current_user: Annotated[User, Depends(UserService().get_current_user)],
) -> dict:
    await UserService().delete_user(current_user)
    return {"success": "ok"}


@users_router.post("/email/send")
async def send_verification_code(
    current_user: Annotated[User, Depends(UserService().get_current_user)]
) -> dict:
    await UserService().create_or_update_code(current_user)
    return {"success": "ok"}


@users_router.post("/email/verify")
async def verify_email(
    current_user: Annotated[User, Depends(UserService().get_current_user)], code: str
) -> UserResponse:
    user = await UserService().verify_email(code, current_user)
    return UserResponse.model_validate(user)


@users_router.post("/email/send/password")
async def send_url_for_refresh_password(email: Annotated[str, Form()]) -> dict:
    await UserService().send_url_for_refresh_password(email)
    return {"success": "ok"}


@users_router.post("/refresh/password")
async def refresh_password(
    token: Annotated[str, Header()],
    new_password: Annotated[str, Form()],
) -> dict:
    await UserService().set_password(token, new_password)
    return {"success": "ok"}


@users_router.put("")
async def update_user(
    current_user: Annotated[User, Depends(UserService().get_current_user)],
    user_update: UserUpdate,
) -> UserResponse:
    user = await UserService().update(current_user, user_update)
    return UserResponse.model_validate(user)


@users_router.get("/email")
async def get_user_by_email(email: str) -> UserResponse:
    user = await UserService().get_user_by_email(email)
    return UserResponse.model_validate(user)
