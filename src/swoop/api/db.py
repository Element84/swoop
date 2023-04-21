import asyncpg
from .config import Settings

async def connect_to_db(settings: Settings) -> None:
    """Connect to Database."""
    db = DB()
    readpool = await db.create_pool(settings.reader_connection_string, settings)
    writepool = await db.create_pool(settings.writer_connection_string, settings)
    return readpool, writepool

async def close_db_connection(pools) -> None:
    """Close connection."""
    await pools.readpool.close()
    await pools.writepool.close()

class DB:
    """DB class that can be used with context manager."""

    connection_string = None
    _pool = None
    _connection = None

    async def create_pool(self, connection_string: str, settings):
        """Create a connection pool."""
        pool = await asyncpg.create_pool(
            connection_string,
            min_size=settings.db_min_conn_size,
            max_size=settings.db_max_conn_size,
            max_queries=settings.db_max_queries,
            max_inactive_connection_lifetime=settings.db_max_inactive_conn_lifetime,
        )
        return pool