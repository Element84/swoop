import asyncio
import inspect
import logging
import random
import string
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from swoop.db import SwoopDB

from swoop.api.app import get_app
from swoop.api.config import Settings
from swoop.api.io import IOClient

logger = logging.getLogger(__name__)


def syncrun(coroutine):
    return asyncio.run(coroutine)


@pytest.fixture(scope="session")
def io_fixture_dir(pytestconfig) -> Path:
    return pytestconfig.rootpath.joinpath("tests", "fixtures", "io")


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

        ioclient = IOClient(
            settings.s3_endpoint,
            settings.access_key_id,
            settings.secret_access_key,
            bucket_name,
        )

        def setup_io(ioclient):
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

        try:
            ioclient.create_bucket(bucket_name)
            setup_io(ioclient)
            yield bucket_name
        finally:
            ioclient.delete_objects()
            ioclient.delete_bucket(bucket_name)

    return io_fixture


def generate_db_fixture(fixtures, db_postfix=None, scope="module"):
    @pytest.fixture(scope=scope)
    def db_fixture(settings):
        nonlocal db_postfix
        nonlocal fixtures
        swoopdb = SwoopDB()

        db_postfix = (
            "".join(random.choices(string.ascii_letters, k=5))
            if not db_postfix
            else db_postfix
        )
        db_name = settings.db_name + "_" + db_postfix

        async def setup_db():
            async with swoopdb.get_db_connection(database=db_name) as conn:
                await swoopdb.load_schema(conn=conn)
                for fixture in fixtures:
                    await swoopdb.load_fixture(fixture, conn=conn)

        try:
            syncrun(swoopdb.create_database(db_name))
            syncrun(setup_db())
            yield db_name
        finally:
            syncrun(swoopdb.drop_database(db_name))

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
    return app


@pytest.fixture
def test_client(test_app):
    with TestClient(test_app) as client:
        yield client
