import pytest

from ..conftest import inject_database_fixture

inject_database_fixture(["base_01"], __name__)

@pytest.fixture
def all_payloads():
    return {
        "payloads": [
            {
                "payload_uuid": "ade69fe7-1d7d-472e-9f36-7242cc2aca77",
            }
        ],
        "links": [
            {
                "href": "http://www.example.com",
                "rel": None,
                "type": None,
                "hreflang": None,
                "title": None,
            }
        ],
    }

@pytest.fixture
def no_payloads_exception():
    return {'detail': 'No payloads that match query parameters found'}

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
async def test_get_payloads_filter_limit_process_only(test_client):
    response = test_client.get("/payloads/?limit=1000&process_id=some_workflow")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_get_payloads_filter_limit_process_collection_only(test_client):
    response = test_client.get("/payloads/?limit=1000&process_id=some_workflow&collection_id=collection1")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_get_payloads_filter_invalid_collection_id(test_client, no_payloads_exception):
    response = test_client.get("/payloads/?limit=1000&process_id=some_workflow&collection_id=collection5")
    assert response.json() == no_payloads_exception
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_get_payloads_filter_invalid_item_id(test_client, no_payloads_exception):
    response = test_client.get("/payloads/?limit=1000&process_id=some_workflow&collection_id=collection1&item_id=id5")
    assert response.json() == no_payloads_exception
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_get_payloads_filter_all(test_client):
    response = test_client.get("/payloads/?limit=1000&process_id=some_workflow&collection_id=collection1&item_id=id1")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_get_payloads_filter_collection_multiple_items(test_client):
    response = test_client.get("/payloads/?limit=1000&process_id=some_workflow&collection_id=collection1&item_id=id1&item_id=id2&item_id=id3")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_get_payloads_filter_multiple_collection(test_client):
    response = test_client.get("/payloads/?limit=1000&process_id=some_workflow&collection_id=collection1&collection_id=collection2")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_get_payloads_filter_only_multiple_items(test_client):
    response = test_client.get("/payloads/?limit=1000&item_id=id1&item_id=id2")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_get_payloads_filter_only_invalid_item_id(test_client, no_payloads_exception):
    response = test_client.get("/payloads/?limit=1000&item_id=id8")
    assert response.json() == no_payloads_exception
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_get_payloads_filter_only_invalid_collection_id(test_client, no_payloads_exception):
    response = test_client.get("/payloads/?limit=1000&collection_id=collection3")
    assert response.json() == no_payloads_exception
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_get_payloads_filter_only_invalid_process_id(test_client, no_payloads_exception):
    response = test_client.get("/payloads/?limit=1000&process_id=hello")
    assert response.json() == no_payloads_exception
    assert response.status_code == 404


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
