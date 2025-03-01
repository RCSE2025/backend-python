from pydantic import BaseModel



class Tickets(BaseModel):
    id: int
    title: int
    status: str
    username: str