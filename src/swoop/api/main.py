from fastapi import FastAPI

from swoop.api.config import Settings

from swoop.api.routers import (
    jobs,
    metrics,
    payloads,
    processes,
    root,
)

app: FastAPI = FastAPI()
app.state.settings = Settings()

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
