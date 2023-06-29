import pytest
from fastapi.testclient import TestClient

from ..conftest import inject_database_fixture, inject_io_fixture

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


a_job = {
    "processID": "action_1",
    "type": "process",
    "jobID": "2595f2da-81a6-423c-84db-935e6791046e",
    "status": "successful",
    "created": "2023-04-28T15:49:00+00:00",
    "updated": "2023-04-28T15:49:03+00:00",
    "started": "2023-04-28T15:49:02+00:00",
    "finished": "2023-04-28T15:49:03+00:00",
    "links": [
        {
            "href": "http://testserver/",
            "rel": "root",
            "type": "application/json",
        },
        {
            "href": "http://testserver/jobs/2595f2da-81a6-423c-84db-935e6791046e",
            "rel": "self",
            "type": "application/json",
        },
        {
            "href": "http://testserver/jobs/2595f2da-81a6-423c-84db-935e6791046e/results",
            "rel": "results",
            "type": "application/json",
        },
        {
            "href": "http://testserver/jobs/2595f2da-81a6-423c-84db-935e6791046e/inputs",
            "rel": "inputs",
            "type": "application/json",
        },
        {
            "href": "http://testserver/processes/action_1",
            "rel": "process",
            "type": "application/json",
        },
        {
            "href": "http://testserver/payloadCacheEntries/ade69fe7-1d7d-472e-9f36-7242cc2aca77",
            "rel": "cache",
            "type": "application/json",
        },
    ],
}


another_job = {
    "processID": "action_2",
    "type": "process",
    "jobID": "81842304-0aa9-4609-89f0-1c86819b0752",
    "status": "accepted",
    "created": "2023-04-28T15:49:00+00:00",
    "updated": "2023-04-28T15:49:00+00:00",
    "started": None,
    "finished": None,
    "links": [
        {
            "href": "http://testserver/",
            "rel": "root",
            "type": "application/json",
        },
        {
            "href": "http://testserver/jobs/81842304-0aa9-4609-89f0-1c86819b0752",
            "rel": "self",
            "type": "application/json",
        },
        {
            "href": "http://testserver/jobs/81842304-0aa9-4609-89f0-1c86819b0752/results",
            "rel": "results",
            "type": "application/json",
        },
        {
            "href": "http://testserver/jobs/81842304-0aa9-4609-89f0-1c86819b0752/inputs",
            "rel": "inputs",
            "type": "application/json",
        },
        {
            "href": "http://testserver/processes/action_2",
            "rel": "process",
            "type": "application/json",
        },
        {
            "href": "http://testserver/payloadCacheEntries/ade69fe7-1d7d-472e-9f36-7242cc2aca77",
            "rel": "cache",
            "type": "application/json",
        },
    ],
}


def single_job(request_endpoint: str):
    return {
        "jobs": [
            a_job,
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


def all_jobs(request_endpoint: str):
    return {
        "jobs": [
            another_job,
            a_job,
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


@pytest.mark.asyncio
async def test_get_all_jobs(test_client: TestClient):
    url: str = "/jobs/"
    response = test_client.get(url)
    assert response.status_code == 200
    assert response.json() == all_jobs(url)


@pytest.mark.asyncio
async def test_get_single_job(test_client: TestClient):
    url: str = "/jobs/?limit=1&processID=action_1"
    response = test_client.get(url)
    assert response.status_code == 200
    assert response.json() == single_job(url)


@pytest.mark.asyncio
async def test_get_job_by_process(test_client: TestClient):
    url: str = "/jobs/?processID=action_1"
    response = test_client.get(url)
    assert response.status_code == 200
    assert response.json() == single_job(url)


@pytest.mark.asyncio
async def test_get_job_by_type_filter(test_client: TestClient):
    url: str = "/jobs/?type=argo-workflow"
    response = test_client.get(url)
    assert response.status_code == 200
    assert response.json() == single_job(url)


@pytest.mark.asyncio
async def test_get_job_by_type_filter_does_not_exist(test_client: TestClient):
    url: str = "/jobs/?type=doesnotexist"
    response = test_client.get(url)
    assert response.status_code == 200
    assert response.json()["jobs"] == []


@pytest.mark.asyncio
async def test_get_job_by_job_id_filter(test_client: TestClient):
    url: str = "/jobs/?jobID=2595f2da-81a6-423c-84db-935e6791046e"
    response = test_client.get(url)
    assert response.status_code == 200
    assert response.json() == single_job(url)


@pytest.mark.asyncio
async def test_get_job_by_status_filter(test_client: TestClient):
    url: str = "/jobs/?status=successful"
    response = test_client.get(url)
    assert response.status_code == 200
    assert response.json() == single_job(url)


@pytest.mark.asyncio
async def test_get_job_by_swoop_status_filter(test_client: TestClient):
    url: str = "/jobs/?swoopStatus=SUCCESSFUL"
    response = test_client.get(url)
    assert response.status_code == 200
    assert response.json() == single_job(url)


@pytest.mark.asyncio
async def test_get_job_by_process_id_job_id_filter(test_client: TestClient):
    url: str = "/jobs/?processID=action_1&jobID=2595f2da-81a6-423c-84db-935e6791046e"
    response = test_client.get(url)
    assert response.status_code == 200
    assert response.json() == single_job(url)


@pytest.mark.asyncio
async def test_get_job_by_process_id_job_id_filter_no_match(test_client: TestClient):
    url: str = "/jobs/?processID=action_1&jobID=81842304-0aa9-4609-89f0-1c86819b0752"
    response = test_client.get(url)
    assert response.status_code == 200
    assert response.json()["jobs"] == []


@pytest.mark.asyncio
async def test_get_job_by_process_id_type_filter(test_client: TestClient):
    url: str = "/jobs/?processID=action_1&type=argo-workflow"
    response = test_client.get(url)
    assert response.status_code == 200
    assert response.json() == single_job(url)


@pytest.mark.asyncio
async def test_get_job_by_process_id_status_filter(test_client: TestClient):
    url: str = "/jobs/?processID=action_1&status=successful"
    response = test_client.get(url)
    assert response.status_code == 200
    assert response.json() == single_job(url)


@pytest.mark.asyncio
async def test_get_job_by_process_id_swoop_status_filter(test_client: TestClient):
    url: str = "/jobs/?processID=action_1&swoopStatus=SUCCESSFUL"
    response = test_client.get(url)
    assert response.status_code == 200
    assert response.json() == single_job(url)


@pytest.mark.asyncio
async def test_get_job_by_type_job_id_filter(test_client: TestClient):
    url: str = "/jobs/?type=argo-workflow&jobID=2595f2da-81a6-423c-84db-935e6791046e"
    response = test_client.get(url)
    assert response.status_code == 200
    assert response.json() == single_job(url)


@pytest.mark.asyncio
async def test_get_job_by_type_job_id_filter_no_match(test_client: TestClient):
    url: str = "/jobs/?type=argo-workflow&jobID=81842304-0aa9-4609-89f0-1c86819b0752"
    response = test_client.get(url)
    assert response.status_code == 200
    assert response.json()["jobs"] == []


@pytest.mark.asyncio
async def test_get_job_by_job_id_status_filter(test_client: TestClient):
    url: str = "/jobs/?jobID=2595f2da-81a6-423c-84db-935e6791046e&status=successful"
    response = test_client.get(url)
    assert response.status_code == 200
    assert response.json() == single_job(url)


@pytest.mark.asyncio
async def test_get_job_by_job_id_status_filter_no_match(test_client: TestClient):
    url: str = "/jobs/?jobID=2595f2da-81a6-423c-84db-935e6791046e&status=running"
    response = test_client.get(url)
    assert response.status_code == 200
    assert response.json()["jobs"] == []


@pytest.mark.asyncio
async def test_get_job_by_job_id_swoop_status_filter(test_client: TestClient):
    url: str = (
        "/jobs/?jobID=2595f2da-81a6-423c-84db-935e6791046e&swoopStatus=SUCCESSFUL"
    )
    response = test_client.get(url)
    assert response.status_code == 200
    assert response.json() == single_job(url)


@pytest.mark.asyncio
async def test_get_job_by_job_id_swoop_status_filter_no_match(test_client: TestClient):
    url: str = "/jobs/?jobID=2595f2da-81a6-423c-84db-935e6791046e&swoopStatus=CANCELED"
    response = test_client.get(url)
    assert response.status_code == 200
    assert response.json()["jobs"] == []


@pytest.mark.asyncio
async def test_get_job_by_status_and_swoop_status_filter_match(test_client: TestClient):
    url: str = "/jobs/?status=successful&swoopStatus=SUCCESSFUL"
    response = test_client.get(url)
    assert response.status_code == 200
    assert response.json() == single_job(url)


@pytest.mark.asyncio
async def test_get_job_by_status_and_swoop_status_filter_contradict(
    test_client: TestClient,
):
    url: str = "/jobs/?status=accepted&swoopStatus=SUCCESSFUL"
    response = test_client.get(url)
    assert response.status_code == 200
    assert response.json()["jobs"] == []


@pytest.mark.asyncio
async def test_get_job_by_datetime_filter(
    test_client: TestClient,
):
    url: str = "/jobs/?datetime=2023-04-28T15:49:00.000000Z"
    response = test_client.get(url)
    assert response.status_code == 200
    assert len(response.json()["jobs"]) == 2


@pytest.mark.asyncio
async def test_get_job_by_datetime_interval_filter(
    test_client: TestClient,
):
    url: str = "/jobs/?datetime=2023-04-01T15:49:00.000000Z/2023-04-30T15:49:00.000000Z"
    response = test_client.get(url)
    assert response.status_code == 200
    assert len(response.json()["jobs"]) == 2


@pytest.mark.asyncio
async def test_get_job_by_datetime_interval_end_open(
    test_client: TestClient,
):
    url: str = "/jobs/?datetime=2023-04-01T15:49:00.000000Z/.."
    response = test_client.get(url)
    assert response.status_code == 200
    assert len(response.json()["jobs"]) == 2


@pytest.mark.asyncio
async def test_get_job_by_datetime_interval_start_open(
    test_client: TestClient,
):
    url: str = "/jobs/?datetime=../2023-04-30T15:49:00.000000Z"
    response = test_client.get(url)
    assert response.status_code == 200
    assert len(response.json()["jobs"]) == 2


@pytest.mark.asyncio
async def test_get_job_by_datetime_interval_filter_no_match(
    test_client: TestClient,
):
    url: str = "/jobs/?datetime=2023-03-01T15:49:00.000000Z/2023-03-30T15:49:00.000000Z"
    response = test_client.get(url)
    assert response.status_code == 200
    assert len(response.json()["jobs"]) == 0


@pytest.mark.asyncio
async def test_get_job_by_datetime_filter_invalid(
    test_client: TestClient,
):
    url: str = "/jobs/?datetime=2023-03-0115:49:00.000000Z"
    response = test_client.get(url)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_job_by_process_id_datetime_filter(
    test_client: TestClient,
):
    url: str = "/jobs/?processID=action_1&datetime=2023-04-28T15:49:00.000000Z"
    response = test_client.get(url)
    assert len(response.json()["jobs"]) == 1


@pytest.mark.asyncio
async def test_get_job_by_job_id_datetime_filter(
    test_client: TestClient,
):
    url: str = "/jobs/?jobID=2595f2da-81a6-423c-84db-935e6791046e&\
    datetime=2023-04-28T15:49:00.000000Z"
    response = test_client.get(url)
    assert len(response.json()["jobs"]) == 1


@pytest.mark.asyncio
async def test_get_job_by_job_id(test_client: TestClient):
    response = test_client.get(
        "/jobs/2595f2da-81a6-423c-84db-935e6791046e",
    )
    assert response.status_code == 200
    assert response.json() == a_job


@pytest.mark.asyncio
async def test_get_job_by_job_id_404(test_client: TestClient):
    response = test_client.get(
        "/jobs/00000000-1111-2222-3333-444444444444/results",
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_job_results(test_client: TestClient):
    response = test_client.get(
        "/jobs/2595f2da-81a6-423c-84db-935e6791046e/results",
    )
    assert response.status_code == 200
    assert response.json() == {
        "process_id": "2595f2da-81a6-423c-84db-935e6791046e",
        "payload": "test_output",
    }


@pytest.mark.asyncio
async def test_get_job_results_404(test_client: TestClient):
    response = test_client.get(
        "/jobs/00000000-1111-2222-3333-444444444444/results",
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_job_payload(test_client: TestClient):
    response = test_client.get(
        "/jobs/2595f2da-81a6-423c-84db-935e6791046e/inputs",
    )
    assert response.status_code == 200
    assert response.json() == {
        "process_id": "2595f2da-81a6-423c-84db-935e6791046e",
        "payload": "test_input",
    }


@pytest.mark.asyncio
async def test_get_job_payload_404(test_client: TestClient):
    response = test_client.get(
        "/jobs/00000000-1111-2222-3333-444444444444/payload",
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_job_status(test_client: TestClient):
    response = test_client.get(
        "/jobs/2595f2da-81a6-423c-84db-935e6791046e",
    )
    assert response.status_code == 200
    assert response.json() == a_job


@pytest.mark.asyncio
async def test_get_job_status_404(test_client: TestClient):
    response = test_client.get(
        "/jobs/00000000-1111-2222-3333-444444444444",
    )
    assert response.status_code == 404
