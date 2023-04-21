from fastapi import FastAPI

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
