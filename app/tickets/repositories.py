from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database.engine import with_async_session
from .models import Ticket


class TicketsRepository:
    """Repository for managing Ticket objects."""

    @with_async_session
    async def create(self, ticket: Ticket, session: AsyncSession) -> None:
        session.add(ticket)
        await session.commit()

    @with_async_session
    async def update(
        self, user: User, user_update: UserUpdate, session: AsyncSession
    ) -> Ticket:
        user = await session.merge(user)
        await session.execute(
            update(User)
            .where(User.id == user.id)
            .values(user_update.model_dump(exclude_none=True))
        )
        await session.commit()
        await session.refresh(user)
        return user

    async def get_all(self) -> sequ: