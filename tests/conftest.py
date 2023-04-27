import asyncio
import random
import string

import asyncpg
import pytest

from pathlib import Path

from swoop.api.config import Settings


@pytest.fixture(scope="session")
def dbschema(pytestconfig) -> Path:
    return pytestconfig.rootpath.joinpath("db", "schema.sql")


@pytest.fixture(scope="session")
def settings() -> Settings:
    return Settings()


async def async_create_database(db_name: str, db_connection_string: str) -> None:
    conn = None
    try:
        conn = await asyncpg.connect(db_connection_string)
        await conn.execute(f'CREATE DATABASE "{db_name}";')
    finally:
        if conn:
            await conn.close()


def create_database(db_name: str, db_connection_string: str) -> None:
    asyncio.run(async_create_database(db_name, db_connection_string))


async def async_load_schema(schema: Path, db_connection_string: str) -> None:
    conn = None
    try:
        conn = await asyncpg.connect(db_connection_string)
        await conn.execute(schema.read_text())
    finally:
        if conn:
            await conn.close()


def load_schema(schema: Path, db_connection_string: str) -> None:
    asyncio.run(async_load_schema(schema, db_connection_string))


async def async_drop_database(db_name: str, db_connection_string: str) -> None:
    conn = None
    try:
        conn = await asyncpg.connect(db_connection_string)
        await conn.execute(f'DROP DATABASE "{db_name}";')
    finally:
        if conn:
            await conn.close()


def drop_database(db_name: str, db_connection_string: str) -> None:
    asyncio.run(async_drop_database(db_name, db_connection_string))


@pytest.fixture(scope="module")
def database(dbschema, settings):
    db_name = (
        settings.database_name
        + "_"
        + "".join(random.choices(string.ascii_letters, k=5))
    )
    create_database(db_name, settings.build_db_connection_string(name=""))
    conn_string = settings.build_db_connection_string(name=db_name)
    load_schema(dbschema, conn_string)
    yield conn_string
    drop_database(db_name, settings.build_db_connection_string(name=""))
