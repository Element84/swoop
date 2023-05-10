import pytest

from .conftest import inject_database_fixture, get_db_connection


inject_database_fixture(["base_01"], __name__)


@pytest.mark.asyncio
async def test_hasdb(database):
    async with get_db_connection(database) as conn:
        await conn.execute("select * from swoop.event;")
