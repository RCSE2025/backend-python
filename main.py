from contextlib import asynccontextmanager
from logging import getLogger

import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from config import LOGGING_CONFIG, METRICS, PRODUCTION
from database import database
from regional_agents.routers import regional_agents_router
from regional_agents.services import RegionalAgentsService
from users.routers import user_router
from utils import apply_migrations

logger = getLogger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    apply_migrations()

    # await S3Worker.new_bucket(BUCKET_NAME, ignore_existing=True)

    database_ = app.state.database

    if not database_.is_connected:
        await database_.connect()

    # if RegionalAgents.count() == 0
    await RegionalAgentsService().first_upload_regional_agents()

    yield

    # shutdown

    database_ = app.state.database
    if database_.is_connected:
        await database_.disconnect()


app = FastAPI(lifespan=lifespan, title="App API", debug=not PRODUCTION)
app.state.database = database

if METRICS:
    from prometheus_fastapi_instrumentator import Instrumentator

    Instrumentator().instrument(app).expose(app)

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.options("/{url}")
async def handle_options(url):
    return JSONResponse({"ok": True}, headers={"Access-Control-Allow-Headers": "*"})


@app.exception_handler(Exception)
async def validation_exception_handler(request: Request, err) -> JSONResponse:
    base_error_message = f"Failed to execute: {request.method}: {request.url}"
    return JSONResponse(
        status_code=500,
        content={"message": f"{base_error_message}. Detail: {str(err)}"},
    )


@app.get("/ping")
async def ping_pong():
    return "pong"


app.include_router(user_router)
app.include_router(regional_agents_router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        port=80,
        host="0.0.0.0",
        reload=not PRODUCTION,
        log_config=LOGGING_CONFIG,
    )
