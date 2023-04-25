from fastapi import FastAPI
from swoop.api.config import get_settings
from swoop.api.db import connect_to_db, close_db_connection
import pytest

@pytest.mark.asyncio
async def test_db_connection_pool():
    app: FastAPI = FastAPI()
    app.state.settings = get_settings('.env')
    await connect_to_db(app)

    connections = []

    # Saturate the connection pool
    for i in range(app.state.settings.db_max_conn_size):
        connections.append(await app.state.readpool.acquire())

    # Expecting a Timeout (after 1s), with no connections available
    with pytest.raises(TimeoutError):
        connections.append(await app.state.readpool.acquire(timeout=1))

    # Release all connections
    for c in connections:
        await app.state.readpool.release(c, timeout=1)

    await close_db_connection(app)
    assert True
