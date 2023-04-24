from fastapi import FastAPI
from swoop.api.db import close_db_connection, connect_to_db
from swoop.api.config import get_settings

from swoop.api.routers import (
    jobs,
    metrics,
    payloads,
    processes,
    root,
)

app: FastAPI = FastAPI()

app.state.settings = get_settings()

@app.on_event("startup")
async def startup_event():
    """Connect to database on startup."""
    app.state.readpool, app.state.writepool = await connect_to_db(app.state.settings)

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
