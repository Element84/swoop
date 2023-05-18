import asyncio
import inspect
import logging
import random
import string
from contextlib import asynccontextmanager
from pathlib import Path

import asyncpg
import pytest
from fastapi.testclient import TestClient

from swoop.api.app import get_app
from swoop.api.config import Settings

logger = logging.getLogger(__name__)


def syncrun(coroutine, *args, **kwargs):
    return asyncio.run(coroutine(*args, **kwargs))


@asynccontextmanager
async def get_db_connection(**kwargs):
    conn = None
    try:
        conn = await asyncpg.connect(**kwargs)
        yield conn
    finally:
        if conn:
            await conn.close()


# @asynccontextmanager
# async def get_io_connection(**kwargs):
#     conn = None
#     try:
#         conn = Minio(**kwargs)
#         yield conn
#     finally:
#         if conn:
#             await conn.close()
#             await conn.release_conn()

# async def create_bucket(bucket_name: str) -> None:
#     async with get_io_connection(bucket_name=None) as conn:
#         await conn.make_bucket(bucket_name)


# async def remove_bucket(bucket_name: str) -> None:
#     async with get_io_connection(bucket_name=None) as conn:
#         await conn.remove_bucket(bucket_name)


async def create_database(db_name: str) -> None:
    async with get_db_connection(database=None) as conn:
        await conn.execute(f'CREATE DATABASE "{db_name}";')


async def drop_database(db_name: str) -> None:
    async with get_db_connection(database=None) as conn:
        await conn.execute(f'DROP DATABASE "{db_name}";')


async def load_sqlfile(conn, sqlfile: Path) -> None:
    await conn.execute(sqlfile.read_text())


@pytest.fixture(scope="session")
def dbschema(pytestconfig) -> Path:
    return pytestconfig.rootpath.joinpath("db", "schema.sql")


@pytest.fixture(scope="session")
def db_fixture_dir(pytestconfig) -> Path:
    return pytestconfig.rootpath.joinpath("db", "fixtures")


@pytest.fixture(scope="session")
def settings() -> Settings:
    return Settings()


def generate_db_fixture(fixtures, db_postfix=None, scope="module"):
    @pytest.fixture(scope=scope)
    def db_fixture(dbschema, db_fixture_dir, settings):
        nonlocal db_postfix
        nonlocal fixtures

        db_postfix = (
            "".join(random.choices(string.ascii_letters, k=5))
            if not db_postfix
            else db_postfix
        )
        db_name = settings.db_name + "_" + db_postfix

        async def setup_db():
            async with get_db_connection(database=db_name) as conn:
                await load_sqlfile(conn, dbschema)
                for fixture_name in fixtures:
                    path = db_fixture_dir.joinpath(fixture_name + ".sql")
                    if not path.is_file():
                        raise ValueError(f"Unknown fixture '{fixture_name}'")
                    await load_sqlfile(conn, path)

        try:
            syncrun(create_database, db_name)
            syncrun(setup_db)
            yield db_name
        finally:
            syncrun(drop_database, db_name)

    return db_fixture


def inject_database_fixture(data_fixtures, db_postfix=None, scope="module"):
    # we need the caller's global scope for this hack to work
    # hence the use of the inspect module
    caller_globals = inspect.stack()[1].frame.f_globals
    # for an explanation of this trick and why it works go here:
    # https://github.com/pytest-dev/pytest/issues/2424
    caller_globals["database"] = generate_db_fixture(
        data_fixtures, db_postfix=db_postfix, scope=scope
    )


inject_database_fixture(["base_01"], __name__)


@pytest.fixture
def test_app(database):
    app = get_app()
    app.state.settings.db_name = database
    return app


@pytest.fixture
def test_client(test_app):
    with TestClient(test_app) as client:
        yield client
