from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from ..conftest import inject_database_fixture

inject_database_fixture(["base_01"], __name__)


a_payload = {
    "id": "ade69fe7-1d7d-472e-9f36-7242cc2aca77",
    "payloadHash": "PsqWxdKjAjrV1+BueXnAS1cWIhU=",
    "processID": "some_workflow",
    "invalidAfter": None,
    "links": [
        {
            "href": "http://testserver/",
            "rel": "root",
            "type": "application/json",
        },
        {
            "href": "http://testserver/payloadCacheEntries/ade69fe7-1d7d-472e-9f36-7242cc2aca77",
            "rel": "self",
            "type": "application/json",
        },
    ],
}


a_payload_details = deepcopy(a_payload)
a_payload_details["links"].extend(
    [
        {
            "href": "http://testserver/jobs/2595f2da-81a6-423c-84db-935e6791046e",
            "rel": "job",
            "type": "application/json",
        },
        {
            "href": "http://testserver/jobs/81842304-0aa9-4609-89f0-1c86819b0752",
            "rel": "job",
            "type": "application/json",
        },
    ]
)


def all_payloads(request_endpoint: str):
    return {
        "payloads": [
            a_payload,
        ],
        "links": [
            {
                "href": "http://testserver/",
                "rel": "root",
                "type": "application/json",
            },
            {
                "href": f"http://testserver{request_endpoint}",
                "rel": "self",
                "type": "application/json",
            },
        ],
    }


no_payload_id_exception = {
    "detail": "No payload that matches payload uuid found",
}


# Tests for GET/payloads endpoint


@pytest.mark.asyncio
async def test_get_payloads_no_filter(test_client: TestClient):
    url: str = "/payloadCacheEntries/"
    response = test_client.get(url)
    assert response.json() == all_payloads(url)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_payloads_filter_limit_only(test_client: TestClient):
    url: str = "/payloadCacheEntries/?limit=1000"
    response = test_client.get(url)
    print(response.json())
    assert response.json() == all_payloads(url)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_payloads_filter_limit_process(test_client: TestClient):
    url: str = "/payloadCacheEntries/?limit=1000&processID=some_workflow"
    response = test_client.get(url)
    assert response.json() == all_payloads(url)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_payloads_filter_only_invalid_process_id(test_client: TestClient):
    response = test_client.get("/payloadCacheEntries/?limit=1000&processID=hello")
    assert response.json()["payloads"] == []
    assert response.status_code == 200


# Tests for GET /payloadCacheEntries/{payload-id} endpoint


@pytest.mark.asyncio
async def test_get_payloadid_match(test_client: TestClient):
    response = test_client.get(
        "/payloadCacheEntries/ade69fe7-1d7d-472e-9f36-7242cc2aca77"
    )
    assert response.json() == a_payload_details
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_payloadid_no_match(test_client: TestClient):
    response = test_client.get(
        "/payloadCacheEntries/d5d64165-82df-4836-b78e-af4daee55d38"
    )
    assert response.json() == no_payload_id_exception
    assert response.status_code == 404


# TODO Add payload POST tests
# @pytest.mark.asyncio
# async def test_retrieve_payload_cache_details(test_client: TestClient):
#     response = test_client.post(
#         "/payloadCacheEntries/",
#         content=json.dumps(a_payload),
#     )
#     assert response.status_code == 200
