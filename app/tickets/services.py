from typing import Sequence

from app.tickets.models import Ticket, Comment
from app.tickets.repositories import TicketsRepository, CommentsRepository
from app.tickets.schemas import TicketCreate, TicketUpdate, CommentCreate


class CommentsService:
    """Service layer for managing comments."""

    repository = CommentsRepository()

    async def create(self, ticket_id: int, comment_data: CommentCreate) -> Comment:
        """Create new comment."""
        comment = Comment(
            text=comment_data.text,
            username=comment_data.username,
            ticket_id=ticket_id
        )
        return await self.repository.create(comment)

    async def get_by_ticket_id(self, ticket_id: int) -> Sequence[Comment]:
        """Get all comments for a ticket."""
        return await self.repository.get_by_ticket_id(ticket_id)

    async def delete(self, comment: Comment) -> None:
        """Delete comment."""
        await self.repository.delete(comment)


class TicketsService:
    """Service layer for managing tickets."""

    repository = TicketsRepository()
    comments_service = CommentsService()

    async def get_all(self) -> Sequence[Ticket]:
        """Get all tickets."""
        return await self.repository.get_all()

    async def get_by_id(self, ticket_id: int) -> Ticket:
        """Get ticket by ID."""
        ticket = await self.repository.get_by_id(ticket_id)
        if not ticket:
            raise ValueError(f"Ticket with id {ticket_id} not found")
        return ticket

    async def create(self, ticket_data: TicketCreate) -> Ticket:
        """Create new ticket."""
        ticket = Ticket(
            title=ticket_data.title,
            description=ticket_data.description,
            status=ticket_data.status,
            username=ticket_data.username
        )
        return await self.repository.create(ticket)

    async def update(self, ticket_id: int, ticket_data: TicketUpdate) -> Ticket:
        """Update existing ticket."""
        ticket = await self.get_by_id(ticket_id)
        
        # Update only provided fields
        update_data = ticket_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(ticket, field, value)
        
        return await self.repository.update(ticket)

    async def delete(self, ticket_id: int) -> None:
        """Delete ticket by ID."""
        ticket = await self.get_by_id(ticket_id)
        await self.repository.delete(ticket)

    async def add_comment(self, ticket_id: int, comment_data: CommentCreate) -> Comment:
        """Add comment to ticket."""
        # Verify ticket exists
        await self.get_by_id(ticket_id)
        return await self.comments_service.create(ticket_id, comment_data)

    async def get_comments(self, ticket_id: int) -> Sequence[Comment]:
        """Get all comments for a ticket."""
        # Verify ticket exists
        await self.get_by_id(ticket_id)
        return await self.comments_service.get_by_ticket_id(ticket_id)