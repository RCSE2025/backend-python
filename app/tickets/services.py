from typing import Sequence

from app.tickets.models import Ticket
from app.tickets.repositories import TicketsRepository
from app.tickets.schemas import Tickets


class TicketsService:
    """Service layer for managing tickets."""

    repository = TicketsRepository()

    async def get_all(self) -> Sequence[Ticket]:
        """Get all tickets."""
        return await self.repository.get_all()

    async def get_by_id(self, ticket_id: int) -> Ticket:
        """Get ticket by ID."""
        return await self.repository.get_by_id(ticket_id)

    async def create(self, ticket_data: Tickets) -> Ticket:
        """Create new ticket."""
        ticket = Ticket(
            id=ticket_data.id,
            title=ticket_data.title,
            status=ticket_data.status,
            username=ticket_data.username
        )
        await self.repository.create(ticket)
        return ticket

    async def update(self, ticket_id: int, ticket_data: Tickets) -> Ticket:
        """Update existing ticket."""
        ticket = await self.get_by_id(ticket_id)
        if not ticket:
            raise ValueError(f"Ticket with id {ticket_id} not found")
        
        for field, value in ticket_data.model_dump(exclude={'id'}).items():
            setattr(ticket, field, value)
        
        return await self.repository.update(ticket)

    async def delete(self, ticket_id: int) -> None:
        """Delete ticket by ID."""
        ticket = await self.get_by_id(ticket_id)
        if not ticket:
            raise ValueError(f"Ticket with id {ticket_id} not found")
        
        await self.repository.delete(ticket)