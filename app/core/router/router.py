from fastapi import APIRouter

from app.tickets.api.v1 import tickets_router

api_router = APIRouter(prefix="/api/v1")

INCLUDED_ROUTERS = [
    tickets_router,
]

for ROUTER in INCLUDED_ROUTERS:
    api_router.include_router(ROUTER)
