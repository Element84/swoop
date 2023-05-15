from fastapi import FastAPI

from swoop.api.config import Settings
from swoop.api.db import close_db_connection, connect_to_db
from swoop.api.routers import jobs, metrics, payloads, processes, root
from swoop.api.workflows import init_workflows_config


def get_app() -> FastAPI:
    app: FastAPI = FastAPI()

    app.state.settings = Settings()

    @app.on_event("startup")
    async def startup_event():
        """Connect to database on startup."""
        init_workflows_config(app)
        await connect_to_db(app)

    @app.on_event("shutdown")
    async def shutdown_event():
        """Close database connection."""
        await close_db_connection(app)

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

    return app
