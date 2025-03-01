from typing import Sequence
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database.engine import with_async_session
from .models import Ticket


class TicketsRepository:
    """Repository for managing Ticket objects."""

    @with_async_session
    async def create(self, ticket: Ticket, session: AsyncSession) -> None:
        """Create new ticket."""
        session.add(ticket)
        await session.commit()

    @with_async_session
    async def update(self, ticket: Ticket, session: AsyncSession) -> Ticket:
        """Update existing ticket."""
        ticket = await session.merge(ticket)
        await session.commit()
        await session.refresh(ticket)
        return ticket

    @with_async_session
    async def delete(self, ticket: Ticket, session: AsyncSession) -> None:
        """Delete ticket."""
        await session.delete(ticket)
        await session.commit()

    @with_async_session
    async def get_by_id(self, ticket_id: int, session: AsyncSession) -> Ticket:
        """Get ticket by ID."""
        result = await session.execute(
            select(Ticket).where(Ticket.id == ticket_id)
        )
        return result.scalar_one_or_none()

    @with_async_session
    async def get_all(self, session: AsyncSession) -> Sequence[Ticket]:
        """Get all tickets."""
        result = await session.execute(select(Ticket))
        return result.scalars().all()