import pytest
from fastapi.testclient import TestClient
from swoop.db import SwoopDB

from ..conftest import inject_database_fixture

inject_database_fixture([], __name__)


# sql to insert 101 rows into swoop.payload_cache with the consecutive uuids
# cdc73916-500c-5501-a658-dd706a943500 through cdc73916-500c-5501-a658-dd706a943564
sql: str = """
DO
$$
BEGIN
  FOR i in 0..100 LOOP
    INSERT INTO swoop.payload_cache (
      payload_uuid,
      workflow_name
    ) VALUES (
      encode(overlay(
        uuid_send('cdc73916-500c-5501-a658-dd706a943500'::uuid)
        PLACING substring(int4send(i) FROM 4) FROM 16 FOR 1
      ), 'hex')::uuid,
      'workflow-a'
    );
  END LOOP;
END;
$$;
"""


@pytest.mark.asyncio
async def test_get_payloads_filter_limit_test(test_client: TestClient, database: str):
    await SwoopDB.execute_sql(sql, database=database)

    # get first page
    base_url: str = "/payloadCacheEntries/?limit=50"
    url: str = base_url
    first_id: str = "cdc73916-500c-5501-a658-dd706a943500"
    last_id: str = "cdc73916-500c-5501-a658-dd706a943531"

    response = test_client.get(url)
    json = response.json()
    print(json)
    payloads = json["payloads"]
    next_href = [link for link in json["links"] if link["rel"] == "next"][0]["href"]

    assert len(payloads) == 50
    assert payloads[0]["id"] == first_id
    assert payloads[-1]["id"] == last_id
    assert next_href == f"http://testserver{base_url}&lastID={last_id}"

    # get second page
    url = f"{base_url}&lastID={last_id}"
    first_id = "cdc73916-500c-5501-a658-dd706a943532"
    last_id = "cdc73916-500c-5501-a658-dd706a943563"

    response = test_client.get(url)
    json = response.json()
    payloads = json["payloads"]
    next_href = [link for link in json["links"] if link["rel"] == "next"][0]["href"]

    assert len(payloads) == 50
    assert payloads[0]["id"] == first_id
    assert payloads[-1]["id"] == last_id
    assert next_href == f"http://testserver{base_url}&lastID={last_id}"

    # get last page
    url = f"{base_url}&lastID={last_id}"
    first_id = "cdc73916-500c-5501-a658-dd706a943564"

    response = test_client.get(url)
    json = response.json()
    payloads = json["payloads"]

    # no next
    assert [link for link in json["links"] if link["rel"] == "next"] == []
    assert len(payloads) == 1
    assert payloads[0]["id"] == first_id
