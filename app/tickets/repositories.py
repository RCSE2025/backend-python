from typing import Sequence
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..core.database.engine import with_async_session
from .models import Ticket, Comment


class CommentsRepository:
    """Repository for managing Comment objects."""

    @with_async_session
    async def create(self, comment: Comment, session: AsyncSession) -> Comment:
        """Create new comment."""
        session.add(comment)
        await session.commit()
        await session.refresh(comment)
        return comment

    @with_async_session
    async def delete(self, comment: Comment, session: AsyncSession) -> None:
        """Delete comment."""
        await session.delete(comment)
        await session.commit()

    @with_async_session
    async def get_by_ticket_id(self, ticket_id: int, session: AsyncSession) -> Sequence[Comment]:
        """Get all comments for a ticket."""
        result = await session.execute(
            select(Comment)
            .where(Comment.ticket_id == ticket_id)
            .order_by(Comment.created_at)
        )
        return result.scalars().all()


class TicketsRepository:
    """Repository for managing Ticket objects."""

    @with_async_session
    async def create(self, ticket: Ticket, session: AsyncSession) -> Ticket:
        """Create new ticket."""
        session.add(ticket)
        await session.commit()
        return ticket

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
            select(Ticket)
            .options(selectinload(Ticket.comments))
            .where(Ticket.id == ticket_id)
        )
        return result.scalar_one_or_none()

    @with_async_session
    async def get_all(self, session: AsyncSession) -> Sequence[Ticket]:
        """Get all tickets."""
        result = await session.execute(
            select(Ticket)
            .options(selectinload(Ticket.comments))
        )
        return result.scalars().all()