from pathlib import Path

import pytest
from dbami.db import SqlFile
from swoop.db import SwoopDB

from ..conftest import inject_database_fixture

inject_database_fixture([], __name__)


@pytest.fixture(scope="session")
def api_fixtures_path(pytestconfig) -> Path:
    return pytestconfig.rootpath.joinpath("tests", "api", "fixtures")


@pytest.fixture(scope="session")
def limit_sql_file(api_fixtures_path) -> Path:
    return api_fixtures_path.joinpath("limit.sql")


@pytest.mark.asyncio
async def test_get_payloads_filter_limit_test(test_client, limit_sql_file, database):
    await SwoopDB.run_sqlfile(SqlFile(path=limit_sql_file), database=database)
    response = test_client.get("/payloads/?limit=2")
    assert len(response.json()["payloads"]) == 2
