import asyncpg
import pytest


@pytest.mark.asyncio
async def test_hasdb(database):
    conn = None
    try:
        conn = await asyncpg.connect(database)
        await conn.execute("select * from swoop.event;")
    finally:
        if conn:
            await conn.close()
