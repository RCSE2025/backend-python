import random
from typing import Annotated, Sequence

import aiosmtplib
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.mail.mail import send_mail_async
from app.users.passwords import get_password_hash, verify_password
from app.utils.build_url import change_password_url

from ..core.config import settings
from ..core.lib import main_logger
from ..utils import msg
from .auth import (
    TokenTypesEnum,
    create_access_token,
    create_password_refresh_token,
    create_refresh_token,
    verify_token,
)
from .exceptions import (
    CredentialsException,
    EmailAlreadyVerifiedException,
    EmailNotVerifiedException,
    IncorrectPasswordException,
    UserAlreadyExistsException,
    UserNotFoundException,
)
from .models import User
from .repositories import UsersRepository
from .schemas import RefreshAccessToken, UserCreate, UserUpdate

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/user/token")


class UserService:
    """Service layer for managing users."""

    repository = UsersRepository()

    async def login_user(self, username: str, password: str) -> RefreshAccessToken:
        user = await self.repository.get_by_email(username)

        if not user:
            raise IncorrectPasswordException()

        if not verify_password(password, user.password):
            raise IncorrectPasswordException()

        access_token = create_access_token(user)
        refresh_token = create_refresh_token(user)

        return RefreshAccessToken(
            access_token=access_token, refresh_token=refresh_token
        )

    async def refresh_token(self, refresh_token: str) -> RefreshAccessToken:
        token_data = verify_token(refresh_token, TokenTypesEnum.refresh)
        user = await self.repository.get_by_id(int(token_data.user_id))
        if user is None:
            raise CredentialsException()
        new_access_token = create_access_token(user)
        return RefreshAccessToken(
            access_token=new_access_token, refresh_token=refresh_token
        )

    async def get_current_user(
        self, token: Annotated[str, Depends(oauth2_scheme)]
    ) -> User:
        token_data = verify_token(token, TokenTypesEnum.access)

        user = await self.repository.get_by_id(int(token_data.user_id))
        if user is None:
            raise CredentialsException()
        return user

    async def create(self, user_create: UserCreate) -> (User, RefreshAccessToken):
        user = await self.repository.get_by_email(user_create.email)
        if user is not None:
            raise UserAlreadyExistsException()

        user = User(**user_create.model_dump())
        user.password = get_password_hash(user.password)
        await self.repository.create(user)
        access_token = create_access_token(user)
        refresh_token = create_refresh_token(user)

        await self.create_or_update_code(user)

        return user, RefreshAccessToken(
            access_token=access_token, refresh_token=refresh_token
        )

    async def delete_user(self, user: User) -> None:
        await self.repository.delete_user(user)

    async def get_all_users(self, offset: int = 0, limit: int = 20) -> Sequence[User]:
        res = await self.repository.get_all_users(offset, limit)
        return res

    async def create_or_update_code(self, user: User) -> None:
        """Creates or updates a verification code for a user and sends it via email.

        Args:
            user: The user for whom to create/update the code.
        """
        if user.is_email_verified:
            raise EmailAlreadyVerifiedException()
        new_code = str(random.randint(1, 999999)).rjust(6, "0")

        # print(new_code)

        await self.repository.create_or_update_code(new_code, user)
        try:
            await send_mail_async(
                settings.mail.MAIN_ADDRESS,
                [user.email],
                msg.EMAIL_VERIFY_HEADER,
                msg.EMAIL_VERIFY_TEXT.format(new_code),
            )
        except aiosmtplib.errors.SMTPServerDisconnected as e:
            main_logger.info("Mail server down!", e)

    async def verify_email(self, code: str, user: User) -> User:
        if user.is_email_verified:
            raise EmailAlreadyVerifiedException()
        return await self.repository.verify_email(code, user)

    async def send_url_for_refresh_password(self, email: str) -> None:
        user = await self.repository.get_by_email(email)
        if user is None or not user.is_email_verified:
            raise EmailNotVerifiedException()
        refresh_password_token = create_password_refresh_token(user)
        await send_mail_async(
            settings.mail.MAIN_ADDRESS,
            [user.email],
            msg.REFRESH_PASSWORD_HEADER,
            msg.REFRESH_PASSWORD_TEXT.format(
                change_password_url(refresh_password_token)
            ),
        )

    async def set_password(self, password_token: str, new_password: str) -> None:
        data = verify_token(password_token, TokenTypesEnum.password)
        user = await self.repository.get_by_id(data.user_id)
        await self.repository.set_password(user, new_password)

    async def update(self, user: User, user_update: UserUpdate) -> User:
        return await self.repository.update(user, user_update)

    async def get_user_by_email(self, email: str) -> User:
        user = await self.repository.get_by_email(email)
        if user is None:
            raise UserNotFoundException(email)
        return user
