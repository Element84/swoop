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
  INSERT INTO swoop.payload_cache (
    payload_uuid,
    workflow_name,
    created_at
  ) VALUES (
    'ade69fe7-1d7d-572e-9f36-7242cc2aca77',
    'some_workflow',
    '2023-04-28 15:49:00+00'
  );

  FOR i in 0..100 LOOP
    INSERT INTO swoop.action (
      action_uuid,
      action_type,
      action_name,
      handler_name,
      parent_uuid,
      created_at,
      priority,
      payload_uuid,
      workflow_version,
      handler_type
    ) VALUES (
      encode(overlay(
        uuid_send('0187c88d-a9e0-788c-adcb-c0b951f8be00'::uuid)
        PLACING substring(int4send(i) FROM 4) FROM 16 FOR 1
      ), 'hex')::uuid,
      'workflow',
      'action_1',
      'handler_foo',
      null,
      '2023-04-28 15:49:00+00',
      100,
      'ade69fe7-1d7d-572e-9f36-7242cc2aca77',
      1,
      'argo-workflow'
    );
  END LOOP;
END;
$$;
"""


@pytest.mark.asyncio
async def test_get_jobs_pagination(test_client: TestClient, database: str):
    await SwoopDB.execute_sql(sql, database=database)

    # get first page
    base_url: str = "/jobs?limit=50"
    url: str = base_url
    first_id: str = "0187c88d-a9e0-788c-adcb-c0b951f8be64"
    last_id: str = "0187c88d-a9e0-788c-adcb-c0b951f8be33"

    response = test_client.get(url)
    json = response.json()
    payloads = json["jobs"]
    next_href = [link for link in json["links"] if link["rel"] == "next"][0]["href"]

    assert len(payloads) == 50
    assert payloads[0]["jobID"] == first_id
    assert payloads[-1]["jobID"] == last_id
    assert next_href == f"http://testserver{base_url}&lastID={last_id}"

    # get second page
    url = f"{base_url}&lastID={last_id}"
    first_id = "0187c88d-a9e0-788c-adcb-c0b951f8be32"
    last_id = "0187c88d-a9e0-788c-adcb-c0b951f8be01"

    response = test_client.get(url)
    json = response.json()
    payloads = json["jobs"]
    next_href = [link for link in json["links"] if link["rel"] == "next"][0]["href"]

    assert len(payloads) == 50
    assert payloads[0]["jobID"] == first_id
    assert payloads[-1]["jobID"] == last_id
    assert next_href == f"http://testserver{base_url}&lastID={last_id}"

    # get last page
    url = f"{base_url}&lastID={last_id}"
    first_id = "0187c88d-a9e0-788c-adcb-c0b951f8be00"

    response = test_client.get(url)
    json = response.json()
    payloads = json["jobs"]

    # no next
    assert [link for link in json["links"] if link["rel"] == "next"] == []
    assert len(payloads) == 1
    assert payloads[0]["jobID"] == first_id
