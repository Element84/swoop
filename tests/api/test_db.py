from swoop.api.config import get_settings
from swoop.api.db import close_db_connection, connect_to_db
import pytest

@pytest.mark.asyncio
async def test_db_connection_pool():
    settings = get_settings('.env')

    pools = await connect_to_db(settings)
    readpool = pools[0]

    for i in range(0, settings.db_max_conn_size):
        await readpool.acquire()

    # No connections available, this should Timeout after 1s
    with pytest.raises(TimeoutError):
        await readpool.acquire(timeout=1)

    readpool.close()
    assert True