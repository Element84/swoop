import asyncpg
from fastapi import FastAPI
from swoop.api.config import Settings


async def connect_to_db(app: FastAPI) -> None:
    """Connect to Database."""
    app.state.readpool = await create_pool(app.state.settings.reader_connection_string, app.state.settings)
    app.state.writepool = await create_pool(app.state.settings.writer_connection_string, app.state.settings)


async def close_db_connection(app: FastAPI) -> None:
    """Close connection."""
    await app.state.readpool.close()
    await app.state.writepool.close()


async def create_pool(connection_string: str, settings: Settings):
    """Create a connection pool."""
    return await asyncpg.create_pool(
        connection_string,
        min_size=settings.db_min_conn_size,
        max_size=settings.db_max_conn_size,
        max_queries=settings.db_max_queries,
        max_inactive_connection_lifetime=settings.db_max_inactive_conn_lifetime,
    )
