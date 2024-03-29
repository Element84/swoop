import pytest
from swoop.db import SwoopDB

from .conftest import inject_database_fixture

inject_database_fixture(["base_01"], __name__)


@pytest.mark.asyncio
async def test_hasdb(database):
    async with SwoopDB.get_db_connection(database=database) as conn:
        await conn.execute("select * from swoop.event;")
