from typing import Optional

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class CommentBase(BaseModel):
    text: str
    username: str


class CommentCreate(CommentBase):
    pass


class Comment(CommentBase):
    id: int
    created_at: datetime
    ticket_id: int

    class Config:
        from_attributes = True


class TicketBase(BaseModel):
    title: str
    description: str
    status: str
    username: str


class TicketCreate(TicketBase):
    pass


class TicketUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class Ticket(TicketBase):
    id: int
    created_at: datetime
    updated_at: datetime
    comments: List[Comment] = []

    class Config:
        from_attributes = True
class UpdateTicket(BaseModel):
    title: Optional[str]
    status: Optional[str]