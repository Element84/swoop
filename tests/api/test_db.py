from swoop.api.config import get_settings
from swoop.api.db import connect_to_db
import pytest

@pytest.mark.asyncio
async def test_db_connection_pool():
    settings = get_settings('.env')

    pools = await connect_to_db(settings)
    readpool = pools[0]

    # Saturate the connection pool
    for i in range(settings.db_max_conn_size):
        await readpool.acquire()

    # Expecting a Timeout (after 1s), with no connections available
    with pytest.raises(TimeoutError):
        await readpool.acquire(timeout=1)

    readpool.close()
    assert True