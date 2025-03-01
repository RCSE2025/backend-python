from app.tickets.repositories import TicketsRepository


class TicketsService:
    """Service layer for managing users."""

    repository = TicketsRepository()

    async def get_all(self) -> Seq: