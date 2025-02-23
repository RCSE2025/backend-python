from datetime import datetime, timedelta, timezone
from typing import List, Optional

from ormar import MultipleMatches

from config import VERIFICATION_CODE_EXPIRE_MINUTES
from users import exceptions
from users.passwords import get_password_hash

from .exceptions import RepositoryUserAlreadyExistsException
from .models import AgentStatusEnum, User, UserRoleEnum, VerificationCode
from .schemas import UserCreate, UserUpdate


class UserRepository:
    """Repository for managing User objects."""

    @staticmethod
    async def create(user_create: UserCreate) -> User:
        """Creates a new user.

        Args:
            user_create: UserCreate schema containing user data.

        Returns:
            The created User object.

        Raises:
            RepositoryUserAlreadyExistsException: If a user with the same email already exists.
        """
        if await User.objects.get_or_none(email=user_create.email):
            raise RepositoryUserAlreadyExistsException()

        password = user_create.password
        user_create.password = get_password_hash(
            password
        )  # Hash the password before saving

        user = User(**user_create.model_dump())
        await user.save()

        return user

    @staticmethod
    async def get_by_email(email: str) -> Optional[User]:
        """Retrieves a user by email. Handles potential multiple matches.

        Args:
            email: The user's email address.

        Returns:
            The User object, or None if not found.
        """
        try:
            # Try to get the user; if only one exists, this will succeed.
            if user := await User.objects.get_or_none(email=email):
                return user
        except MultipleMatches:
            # Handle the case where multiple users have the same email - returns the first one.
            return await User.objects.first(email=email)

    @staticmethod
    async def get_by_id(user_id: int) -> Optional[User]:
        """Retrieves a user by ID.

        Args:
            user_id: The user's ID.

        Returns:
            The User object, or None if not found.
        """
        return await User.objects.get_or_none(id=user_id)

    @staticmethod
    async def delete_user(user: User) -> None:
        """Deletes a user.

        Args:
            user: The User object to delete.
        """
        await user.delete()

    @staticmethod
    async def get_all_users(offset: int = 0, limit: int = 20) -> List[User]:
        """Retrieves all users with pagination.

        Args:
            offset: The offset for pagination.
            limit: The limit for pagination.

        Returns:
            A list of User objects.
        """
        return await User.objects.limit(limit).offset(offset).all()

    @staticmethod
    async def create_or_update_code(code: str, user: User) -> None:
        """Creates or updates a verification code for a user.

        Args:
            code: The verification code.
            user: The User object.
        """

        verification_code, _ = await VerificationCode.objects.get_or_create(
            user=user.id, _defaults={"code": code}
        )
        new_date = datetime.now(timezone.utc)
        await verification_code.update(
            send_at=new_date,
            expired_at=new_date + timedelta(minutes=VERIFICATION_CODE_EXPIRE_MINUTES),
            code=code,
        )

    @staticmethod
    async def verify_email(code: str, user: User) -> User:
        """Verifies a user's email address using a verification code.

        Args:
            code: The verification code.
            user: The User object.

        Returns:
            The updated User object.

        Raises:
            CodeNotExistsException: If the verification code does not exist.
            CodeExpiredException: If the verification code has expired.
            CodeIncorrectException: If the verification code is incorrect.
        """
        verification_code = await VerificationCode.objects.get_or_none(user=user.id)
        if verification_code is None:
            raise exceptions.CodeNotExistsException()
        if verification_code.expired_at < datetime.now(timezone.utc):
            raise exceptions.CodeExpiredException()
        if verification_code.code != code:
            raise exceptions.CodeIncorrectException()

        user = await user.update(is_email_verified=True)
        return user

    @staticmethod
    async def set_password(user: User, new_password: str) -> None:
        """Sets a new password for a user.

        Args:
            user: The User object.
            new_password: The new password.
        """
        await user.update(password=get_password_hash(new_password))

    @staticmethod
    async def update(user: User, user_update: UserUpdate) -> User:
        """Updates a user.

        Args:
            user: The User object to update.
            user_update: UserUpdate schema containing update data.

        Returns:
            The updated User object.
        """
        return await user.update(**user_update.model_dump(exclude_unset=True))

    @staticmethod
    async def set_status(user: User, status: AgentStatusEnum) -> User:
        """Sets the status of a user.

        Args:
            user: The User object.
            status: The new status.

        Returns:
            The updated User object.
        """
        user = await user.update(status=status)
        return user

    @staticmethod
    async def get_users_by_status(status: AgentStatusEnum) -> List[User]:
        """Retrieves users by status, filtering for agents only.

        Args:
            status: The status to filter by.

        Returns:
            A list of User objects.
        """
        execute = User.objects.filter(role=UserRoleEnum.AGENT.value)
        if status:
            execute = execute.filter(status=status.value)
        return await execute.all()
