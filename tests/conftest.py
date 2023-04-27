import asyncio
import random
import string

import asyncpg
import pytest

from pathlib import Path

from contextlib import asynccontextmanager

import pytest_asyncio
from swoop.api.config import Settings
from swoop.api.main import app


@asynccontextmanager
async def get_db_connection(db_connection_string: str) -> None:
    conn = None
    try:
        conn = await asyncpg.connect(db_connection_string)
        yield conn
    finally:
        if conn:
            await conn.close()


async def create_database(db_name: str, db_connection_string: str) -> None:
    async with get_db_connection(db_connection_string) as conn:
        await conn.execute(f'CREATE DATABASE "{db_name}";')


async def load_schema(schema: Path, db_connection_string: str) -> None:
    async with get_db_connection(db_connection_string) as conn:
        await conn.execute(schema.read_text())


async def load_data(db_connection_string: str) -> None:
    async with get_db_connection(db_connection_string) as conn:
        inserted = await conn.copy_records_to_table(
            table_name='action',
            schema_name='swoop',
            columns=['action_uuid', 'action_type', 'action_name', 'handler_name', 'parent_uuid', 'priority'],
            records=[
            ('2595f2da-81a6-423c-84db-935e6791046e','callback','foo_name','handler_foo',5001,100),
            ('81842304-0aa9-4609-89f0-1c86819b0752','callback','foo_name','handler_foo',5001,100)
            ],
        )

        # inserted = await conn.copy_to_table(
        #     table_name='action',
        #     schema_name='swoop',
        #     source='tests/fixtures/action.csv',
        #     #header=True,
        #     columns=['action_uuid', 'action_type', 'action_name', 'handler_name', 'parent_uuid', 'priority']
        # )

        print (f'Insert Result: {inserted}')


async def drop_database(db_name: str, db_connection_string: str) -> None:
    async with get_db_connection(db_connection_string) as conn:
        await conn.execute(f'DROP DATABASE "{db_name}";')


# If using pytest_asyncio fixtures, the event_loop scope must at least match
# the scope of those fixtures (currently "module")
@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def dbschema(pytestconfig) -> Path:
    return pytestconfig.rootpath.joinpath("db", "schema.sql")


# Will set a unique database name (settings.database_url) per module
@pytest.fixture(scope="module")
def settings() -> Settings:
    return Settings()


@pytest_asyncio.fixture(scope="module")
async def test_app(database):
    app.state.settings.database_url = database
    return app


@pytest_asyncio.fixture(scope="module")
async def database(dbschema, settings):
    db_name = (
        settings.database_name
        + "_"
        + "".join(random.choices(string.ascii_letters, k=5))
    )
    await create_database(db_name, settings.build_db_connection_string(name=""))
    conn_string = settings.build_db_connection_string(name=db_name)
    await load_schema(dbschema, conn_string)
    await load_data(conn_string)
    yield conn_string
    await drop_database(db_name, settings.build_db_connection_string(name=""))
