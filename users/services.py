import random
from typing import Annotated, List

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

import msg
from config import MAIL_MAIN_ADDRESS
from mail.mail import send_mail_async
from users.passwords import verify_password
from utils.build_url import change_password_url, create_regional_agent_url

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
    UserNotRootException,
)
from .models import AgentStatusEnum, User, UserRoleEnum
from .repositories import RepositoryUserAlreadyExistsException, UserRepository
from .schemas import RefreshAccessToken, UserCreate, UserUpdate

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/token")


class UserService:
    """Service layer for managing users."""

    repository = UserRepository()

    async def login_user(self, username: str, password: str) -> RefreshAccessToken:
        """Logs in a user and returns access and refresh tokens.

        Args:
            username: The user's email address.
            password: The user's password.

        Returns:
            A RefreshAccessToken object containing the access and refresh tokens.

        Raises:
            IncorrectPasswordException: If the password is incorrect.
        """
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
        """Refreshes an access token using a refresh token.

        Args:
            refresh_token: The refresh token.

        Returns:
            A RefreshAccessToken object containing the new access token and the original refresh token.

        Raises:
            CredentialsException: If the refresh token is invalid or expired.
        """

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
        """Retrieves the current user using a JWT access token.

        Args:
            token: The JWT access token.

        Returns:
            The User object.

        Raises:
            CredentialsException: If the token is invalid or expired.
        """
        token_data = verify_token(token, TokenTypesEnum.access)

        user = await self.repository.get_by_id(int(token_data.user_id))
        if user is None:
            raise CredentialsException()
        return user

    async def create(self, user_create: UserCreate) -> (User, RefreshAccessToken):
        """Creates a new user and returns access and refresh tokens.

        Args:
            user_create: UserCreate schema containing user data.

        Returns:
            A tuple containing the created User object and a RefreshAccessToken object.

        Raises:
            UserAlreadyExistsException: If a user with the same email already exists.
            UserNotRootException: if user tries to create root user.
        """
        try:
            if user_create.role == UserRoleEnum.ROOT:
                raise UserNotRootException()

            user = await self.repository.create(user_create)
        except RepositoryUserAlreadyExistsException:
            raise UserAlreadyExistsException()
        access_token = create_access_token(user)
        refresh_token = create_refresh_token(user)

        await self.create_or_update_code(user)

        return user, RefreshAccessToken(
            access_token=access_token, refresh_token=refresh_token
        )

    async def delete_user(self, user: User) -> None:
        """Deletes a user.

        Args:
            user: The User object to delete.
        """
        await self.repository.delete_user(user)

    async def get_all_users(self, offset: int = 0, limit: int = 20) -> List[User]:
        """Retrieves all users with pagination.

        Args:
            offset: The offset for pagination.
            limit: The limit for pagination.

        Returns:
            A list of User objects.
        """
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

        await send_mail_async(
            MAIL_MAIN_ADDRESS,
            [user.email],
            msg.EMAIL_VERIFY_HEADER,
            msg.EMAIL_VERIFY_TEXT.format(new_code),
        )

        await self.repository.create_or_update_code(new_code, user)

    async def verify_email(self, code: str, user: User) -> User:
        """Verifies a user's email address using a verification code.

        Args:
            code: The verification code.
            user: The User object.

        Returns:
            The updated User object.

        Raises:
            EmailAlreadyVerifiedException: If the user's email is already verified.
        """
        if user.is_email_verified:
            raise EmailAlreadyVerifiedException()
        return await self.repository.verify_email(code, user)

    async def send_url_for_refresh_password(self, email: str) -> None:
        """Sends a password reset link to the user's email address.

        Args:
            email: The user's email address.

        Raises:
            EmailNotVerifiedException: If the user's email is not verified.
        """
        user = await self.repository.get_by_email(email)
        if user is None or not user.is_email_verified:
            raise EmailNotVerifiedException()
        refresh_password_token = create_password_refresh_token(user)
        await send_mail_async(
            MAIL_MAIN_ADDRESS,
            [user.email],
            msg.REFRESH_PASSWORD_HEADER,
            msg.REFRESH_PASSWORD_TEXT.format(
                change_password_url(refresh_password_token)
            ),
        )

    async def set_status(
        self, root: User, user_id: int, status: AgentStatusEnum
    ) -> User:
        """Sets the status of a user.  Requires root privileges.

        Args:
            root: The root user performing the action.
            user_id: The ID of the user whose status to change.
            status: The new status.

        Returns:
            The updated User object.

        Raises:
            UserNotRootException: If the root user does not have root privileges.
            UserNotFoundException: If the user to update is not found.
        """
        if root.role != UserRoleEnum.ROOT.value:  # Use value for direct comparison.
            raise UserNotRootException()
        user = await self.repository.get_by_id(user_id)
        if user is None:
            raise UserNotFoundException(user_id)
        user = await self.repository.set_status(user, status)

        if status == AgentStatusEnum.APPROVED:
            await send_mail_async(
                MAIL_MAIN_ADDRESS,
                [user.email],
                msg.REGIONAL_AGENT_VERIFY_HEADER,
                msg.REGIONAL_AGENT_VERIFY_TEXT.format(create_regional_agent_url()),
            )

        return user

    async def set_password(self, password_token: str, new_password: str) -> None:
        """Sets a new password for a user using a password reset token.

        Args:
            password_token: The password reset token.
            new_password: The new password.

        Raises:
            CredentialsException: If the password reset token is invalid.
        """
        data = verify_token(password_token, TokenTypesEnum.password)
        user = await self.repository.get_by_id(data.user_id)
        await self.repository.set_password(user, new_password)

    async def update(self, user: User, user_update: UserUpdate) -> User:
        """Updates a user.

        Args:
            user: The User object to update.
            user_update: UserUpdate schema containing update data.

        Returns:
            The updated User object.
        """
        return await self.repository.update(user, user_update)

    async def get_users_by_status(
        self, current_user: User, status: AgentStatusEnum
    ) -> List[User]:
        """Retrieves users by status. Requires root privileges.

        Args:
            current_user: The current user performing the action.
            status: The status to filter by.

        Returns:
            A list of User objects.

        Raises:
            UserNotRootException: If the current user does not have root privileges.
        """
        if current_user.role != UserRoleEnum.ROOT.value:
            raise UserNotRootException()

        return await self.repository.get_users_by_status(status)

    async def get_user_by_email(self, email: str) -> User:
        """Retrieves a user by email.

        Args:
            email: The user's email address.

        Returns:
            The User object.

        Raises:
            UserNotFoundException: If the user is not found.
        """
        user = await self.repository.get_by_email(email)
        if user is None:
            raise UserNotFoundException(email)
        return user
