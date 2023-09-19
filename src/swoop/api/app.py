from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from jsonschema import ValidationError

from swoop.api.config import Settings
from swoop.api.db import close_db_connection, connect_to_db
from swoop.api.exceptions import HTTPException
from swoop.api.io import IOClient
from swoop.api.routers import jobs, payloads, processes, root
from swoop.api.workflows import init_workflows_config


def get_app() -> FastAPI:
    app: FastAPI = FastAPI(
        title="swoop-api",
    )

    app.state.settings = Settings()

    @app.on_event("startup")
    async def startup_event():
        """Connect to database on startup."""
        app.state.io = IOClient(
            app.state.settings.bucket_name,
            app.state.settings.s3_endpoint,
        )
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
        prefix="/cache",
    )

    @app.exception_handler(HTTPException)
    async def swoop_http_exception_handler(request: Request, exc: HTTPException):
        return exc.to_json()

    @app.exception_handler(ValidationError)
    async def validation_exception_handler(request: Request, exc: ValidationError):
        status = 422
        return JSONResponse(
            status_code=status,
            content={
                "status": status,
                "detail": exc.message,
                "path": exc.json_path,
            },
        )

    return app
