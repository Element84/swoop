import pytest
from fastapi import FastAPI

from swoop.api.app import get_app
from swoop.api.db import close_db_connection, connect_to_db

from ..conftest import inject_database_fixture

inject_database_fixture(["base_01"], __name__)


@pytest.mark.asyncio
async def test_db_connection_pool() -> None:
    app: FastAPI = get_app()
    await connect_to_db(app)

    connections = []

    # Saturate the connection pool
    for _ in range(app.state.settings.db_max_conn_size):
        connections.append(await app.state.readpool.acquire())

    # Expecting a Timeout (after 1s), with no connections available
    with pytest.raises(TimeoutError):
        connections.append(await app.state.readpool.acquire(timeout=0.1))

    # Release all connections
    for c in connections:
        await app.state.readpool.release(c, timeout=1)

    await close_db_connection(app)
    assert True


@pytest.mark.asyncio
async def test_db_connection_pool_with_reader_host() -> None:
    app: FastAPI = get_app()

    # Testing connection pool with db writer host
    app.state.settings.db_writer_host = app.state.settings.db_reader_host
    await connect_to_db(app)

    connections = []

    # Saturate the connection pool
    for _ in range(app.state.settings.db_max_conn_size):
        connections.append(await app.state.readpool.acquire())

    # Expecting a Timeout (after 1s), with no connections available
    with pytest.raises(TimeoutError):
        connections.append(await app.state.readpool.acquire(timeout=0.1))

    # Release all connections
    for c in connections:
        await app.state.readpool.release(c, timeout=1)

    await close_db_connection(app)
    assert True
