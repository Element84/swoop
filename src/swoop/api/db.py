import asyncpg
from fastapi import FastAPI

from swoop.api.config import Settings


async def connect_to_db(app: FastAPI) -> None:
    """Connect to Database."""
    app.state.writepool = app.state.readpool = await create_pool(
        app.state.settings.db_reader_host,
        app.state.settings,
    )
    if app.state.settings.db_writer_host:
        app.state.writepool = await create_pool(
            app.state.settings.db_writer_host,
            app.state.settings,
        )


async def close_db_connection(app: FastAPI) -> None:
    """Close connection."""
    await app.state.readpool.close()
    await app.state.writepool.close()


async def create_pool(host: str, settings: Settings):
    """Create a connection pool."""
    return await asyncpg.create_pool(
        host=host,
        database=settings.db_name,
        min_size=settings.db_min_conn_size,
        max_size=settings.db_max_conn_size,
        max_queries=settings.db_max_queries,
        max_inactive_connection_lifetime=settings.db_max_inactive_conn_lifetime,
    )
