import asyncio
import random
import string
import logging
import asyncpg
import pytest
import inspect
from pathlib import Path

from contextlib import asynccontextmanager
from fastapi.testclient import TestClient

from swoop.api.config import Settings
from swoop.api.app import get_app


logger = logging.getLogger(__name__)


def syncrun(coroutine, *args, **kwargs):
    return asyncio.run(coroutine(*args, **kwargs))


@asynccontextmanager
async def get_db_connection(db_connection_string: str):
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


async def drop_database(db_name: str, db_connection_string: str) -> None:
    async with get_db_connection(db_connection_string) as conn:
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
        db_name = settings.database_name + "_" + db_postfix
        pg_conn_string = settings.build_db_connection_string(name="")
        conn_string = settings.build_db_connection_string(name=db_name)

        async def setup_db():
            async with get_db_connection(conn_string) as conn:
                await load_sqlfile(conn, dbschema)
                for fixture_name in fixtures:
                    path = db_fixture_dir.joinpath(fixture_name + ".sql")
                    if not path.is_file():
                        raise ValueError(f"Unknown fixture '{fixture_name}'")
                    await load_sqlfile(conn, path)

        try:
            syncrun(create_database, db_name, pg_conn_string)
            syncrun(setup_db)
            yield conn_string
        finally:
            syncrun(drop_database, db_name, pg_conn_string)

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
    app.state.settings.database_url = database
    return app


@pytest.fixture
def test_client(test_app):
    with TestClient(test_app) as client:
        yield client
