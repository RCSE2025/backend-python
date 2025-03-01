from typing import Annotated, List, Sequence

from fastapi import APIRouter, Depends, Form, Header, Query, HTTPException

from app.tickets.models import Ticket, Comment
from app.tickets.schemas import (
    Ticket as TicketSchema,
    TicketCreate,
    TicketUpdate,
    Comment as CommentSchema,
    CommentCreate, TicketBase
)
from app.tickets.services import TicketsService

tickets_router = APIRouter(tags=["tickets"], prefix="/tickets")


@tickets_router.get("/", response_model=List[TicketSchema])
async def get_tickets() -> Sequence[Ticket]:
    """Get all tickets."""
    return await TicketsService().get_all()


@tickets_router.get("/{ticket_id}", response_model=TicketSchema)
async def get_ticket(ticket_id: int) -> Ticket:
    """Get ticket by ID."""
    try:
        return await TicketsService().get_by_id(ticket_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Ticket not found")


@tickets_router.post("/", status_code=201)
async def create_ticket(ticket: TicketCreate):
    """Create new ticket."""
    return await TicketsService().create(ticket)


@tickets_router.patch("/{ticket_id}", response_model=TicketSchema)
async def update_ticket(ticket_id: int, ticket: TicketUpdate) -> Ticket:
    """Update existing ticket."""
    try:
        return await TicketsService().update(ticket_id, ticket)
    except ValueError:
        raise HTTPException(status_code=404, detail="Ticket not found")


@tickets_router.delete("/{ticket_id}", status_code=204)
async def delete_ticket(ticket_id: int) -> None:
    """Delete ticket."""
    try:
        await TicketsService().delete(ticket_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Ticket not found")


# Comments endpoints
@tickets_router.get("/{ticket_id}/comments", response_model=List[CommentSchema])
async def get_ticket_comments(ticket_id: int) -> Sequence[Comment]:
    """Get all comments for a ticket."""
    try:
        return await TicketsService().get_comments(ticket_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Ticket not found")


@tickets_router.post("/{ticket_id}/comments", response_model=CommentSchema, status_code=201)
async def add_ticket_comment(ticket_id: int, comment: CommentCreate) -> Comment:
    """Add comment to ticket."""
    try:
        return await TicketsService().add_comment(ticket_id, comment)
    except ValueError:
        raise HTTPException(status_code=404, detail="Ticket not found")