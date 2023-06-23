import pytest

from ..conftest import inject_database_fixture

inject_database_fixture(["base_01"], __name__)


@pytest.fixture
def all_payloads():
    return {
        "payloads": [
            {
                "payload_id": "ade69fe7-1d7d-472e-9f36-7242cc2aca77",
                "href": "http://testserver/payloads/ade69fe7-1d7d-472e-9f36-7242cc2aca77",
                "type": "payload",
            }
        ],
        "links": [
            {
                "href": "http://www.example.com",
            }
        ],
    }


@pytest.fixture
def no_payload_id_exception():
    return {"detail": "No payload that matches payload uuid found"}


# Tests for GET/payloads endpoint


@pytest.mark.asyncio
async def test_get_payloads_no_filter(test_client, all_payloads):
    response = test_client.get("/payloads")
    assert response.json() == all_payloads
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_payloads_filter_limit_only(test_client, all_payloads):
    response = test_client.get("/payloads/?limit=1000")
    assert response.json() == all_payloads
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_payloads_filter_limit_process(test_client):
    response = test_client.get("/payloads/?limit=1000&processID=some_workflow")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_payloads_filter_only_invalid_process_id(test_client):
    response = test_client.get("/payloads/?limit=1000&processID=hello")
    assert response.json()["payloads"] == []
    assert response.status_code == 200


# Tests for GET/payloads/{payload-id} endpoint


@pytest.mark.asyncio
async def test_get_payloadid_match(test_client):
    response = test_client.get("/payloads/ade69fe7-1d7d-472e-9f36-7242cc2aca77")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_payloadid_no_match(test_client, no_payload_id_exception):
    response = test_client.get("/payloads/d5d64165-82df-4836-b78e-af4daee55d38")
    assert response.json() == no_payload_id_exception
    assert response.status_code == 404
