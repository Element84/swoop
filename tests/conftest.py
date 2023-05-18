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
from swoop.api.io import IOClient

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


def create_bucket(
    s3_endpoint: str, access_key: str, secret_key: str, bucket_name: str
) -> None:
    ioclient = IOClient(s3_endpoint, access_key, secret_key, bucket_name)
    ioclient.create_bucket(bucket_name)


def remove_bucket(
    s3_endpoint: str, access_key: str, secret_key: str, bucket_name: str
) -> None:
    ioclient = IOClient(s3_endpoint, access_key, secret_key, bucket_name)
    ioclient.delete_bucket(bucket_name)


def remove_object(ioclient, object_name: str) -> None:
    ioclient.delete_object(object_name)


def load_jsonfile(ioclient, object_name: str, file_name: str) -> None:
    ioclient.put_file_object(object_name, file_name)


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
def io_fixture_dir(pytestconfig) -> Path:
    return pytestconfig.rootpath.joinpath("io", "fixtures")


@pytest.fixture(scope="session")
def settings() -> Settings:
    return Settings()


def generate_io_fixture(fixtures, io_postfix=None, scope="module"):
    @pytest.fixture(scope=scope)
    def io_fixture(io_fixture_dir, settings):
        nonlocal io_postfix
        nonlocal fixtures

        io_postfix = (
            "".join(random.choices(string.ascii_letters, k=5))
            if not io_postfix
            else io_postfix
        )
        bucket_name = (
            str(settings.bucket_name + "-" + io_postfix)
            .replace(".", "-")
            .replace("_", "-")
        )

        def setup_io():
            ioclient = IOClient(
                settings.s3_endpoint,
                settings.access_key_id,
                settings.secret_access_key,
                bucket_name,
            )
            for fixture in fixtures:
                path = io_fixture_dir.joinpath(fixture["source"])
                if not path.is_dir():
                    raise ValueError(f"Unknown fixture '{str(path)}'")
                files = Path(path).glob("*")
                for file in files:
                    if not file.is_file():
                        raise ValueError(f"Unknown fixture file '{str(file)}'")
                    ioclient.put_file_object(
                        "{}/{}".format(fixture["destination"], file.name),
                        str(file),
                    )

        def cleanup_io():
            ioclient = IOClient(
                settings.s3_endpoint,
                settings.access_key_id,
                settings.secret_access_key,
                bucket_name,
            )
            for fixture in fixtures:
                path = io_fixture_dir.joinpath(fixture["source"])
                if not path.is_dir():
                    raise ValueError(f"Unknown fixture '{str(path)}'")
                files = Path(path).glob("*")
                for file in files:
                    if file.is_file():
                        ioclient.delete_object(
                            "{}/{}".format(fixture["destination"], file.name)
                        )

        try:
            create_bucket(
                settings.s3_endpoint,
                settings.access_key_id,
                settings.secret_access_key,
                bucket_name,
            )
            setup_io()
            yield bucket_name
        finally:
            cleanup_io()
            remove_bucket(
                settings.s3_endpoint,
                settings.access_key_id,
                settings.secret_access_key,
                bucket_name,
            )

    return io_fixture


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


def inject_io_fixture(io_fixtures, io_postfix=None, scope="module"):
    # we need the caller's global scope for this hack to work
    # hence the use of the inspect module
    caller_globals = inspect.stack()[1].frame.f_globals
    # for an explanation of this trick and why it works go here:
    # https://github.com/pytest-dev/pytest/issues/2424
    caller_globals["bucket_name"] = generate_io_fixture(
        io_fixtures, io_postfix=io_postfix, scope=scope
    )


inject_database_fixture(["base_01"], __name__)
inject_io_fixture(
    [
        {
            "source": "base_01",
            "destination": "/execution/2595f2da-81a6-423c-84db-935e6791046e",
        },
        {
            "source": "base_02",
            "destination": "/execution/81842304-0aa9-4609-89f0-1c86819b0752",
        },
    ],
    __name__,
)


@pytest.fixture
def test_app(database, bucket_name):
    app = get_app()
    app.state.settings.db_name = database
    app.state.settings.bucket_name = bucket_name
    app.state.io = IOClient(
        app.state.settings.s3_endpoint,
        app.state.settings.access_key_id,
        app.state.settings.secret_access_key,
        app.state.settings.bucket_name,
    )
    print(app.state.settings)
    return app


@pytest.fixture
def test_client(test_app):
    with TestClient(test_app) as client:
        yield client
