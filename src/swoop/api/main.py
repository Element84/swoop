from fastapi import FastAPI
from .db import close_db_connection, connect_to_db

from swoop.api.config import get_settings

from swoop.api.routers import (
    jobs,
    metrics,
    payloads,
    processes,
    root,
)

settings = get_settings()

app: FastAPI = FastAPI()

app.state.settings = settings

@app.on_event("startup")
async def startup_event():
    """Connect to database on startup."""
    pools = await connect_to_db(settings)
    app.state.readpool = pools[0]
    app.state.writepool = pools[1]

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection."""
    await close_db_connection(app.state)

app.include_router(
    root.router,
)
app.include_router(
    processes.router,
    prefix="/processes",
)
app.include_router(
    jobs.router,
    prefix="/jobs",
)
app.include_router(
    payloads.router,
    prefix="/payloads",
)
app.include_router(
    metrics.router,
)
