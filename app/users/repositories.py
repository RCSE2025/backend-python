from datetime import datetime, timedelta, timezone
from typing import Optional, Sequence

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.users.passwords import get_password_hash

from ..core.config import settings
from ..core.database.engine import with_async_session
from . import exceptions
from .models import User, VerificationCode
from .schemas import UserUpdate


class UsersRepository:
    """Repository for managing User objects."""

    @with_async_session
    async def create(self, user: User, session: AsyncSession) -> None:
        session.add(user)
        await session.commit()

    @with_async_session
    async def get_by_email(self, email: str, session: AsyncSession) -> Optional[User]:
        result = await session.execute(select(User).where(User.email == email))

        user = result.scalars().first()
        return user if user else None

    @with_async_session
    async def get_by_id(self, user_id: int, session: AsyncSession) -> Optional[User]:
        result = await session.execute(select(User).where(User.id == user_id))

        user = result.scalars().first()
        return user if user else None

    @with_async_session
    async def delete_user(self, user: User, session: AsyncSession) -> None:
        await session.execute(delete(User).where(User.id == user.id))
        await session.commit()

    @with_async_session
    async def get_all_users(
        self, *, offset: int = 0, limit: int = 20, session: AsyncSession
    ) -> Sequence[User]:
        result = await session.execute(select(User).offset(offset).limit(limit))
        return result.scalars().all()

    @with_async_session
    async def create_or_update_code(
        self, new_code: str, user: User, session: AsyncSession
    ) -> None:
        code = (
            (
                await session.execute(
                    select(VerificationCode).where(VerificationCode.user_id == user.id)
                )
            )
            .scalars()
            .first()
        )

        if code:
            await session.execute(
                update(VerificationCode)
                .where(VerificationCode.user_id == user.id)
                .values(
                    code=new_code,
                    expired_at=datetime.now()
                    + timedelta(minutes=settings.app.VERIFICATION_CODE_EXPIRE_MINUTES),
                )
            )
        else:
            code = VerificationCode(code=new_code, user_id=user.id)
            session.add(code)
        await session.commit()

    @with_async_session
    async def verify_email(
        self, code: str, user: User, session: AsyncSession
    ) -> User | None:
        verification_code = (
            (
                await session.execute(
                    select(VerificationCode).where(VerificationCode.user_id == user.id)
                )
            )
            .scalars()
            .first()
        )
        if verification_code is None:
            raise exceptions.CodeNotExistsException()
        if verification_code.expired_at < datetime.now(timezone.utc):
            raise exceptions.CodeExpiredException()
        if verification_code.code != code:
            raise exceptions.CodeIncorrectException()

        user = await session.merge(user)
        await session.execute(
            update(User).where(User.id == user.id).values(is_email_verified=True)
        )

        await session.commit()
        await session.refresh(user)
        return user if user else None

    @with_async_session
    async def set_password(
        self, user: User, new_password: str, session: AsyncSession
    ) -> None:
        await session.execute(
            update(User)
            .where(User.id == user.id)
            .values(password=get_password_hash(new_password))
        )
        await session.commit()

    @with_async_session
    async def update(
        self, user: User, user_update: UserUpdate, session: AsyncSession
    ) -> User:
        user = await session.merge(user)
        await session.execute(
            update(User)
            .where(User.id == user.id)
            .values(user_update.model_dump(exclude_none=True))
        )
        await session.commit()
        await session.refresh(user)
        return user
