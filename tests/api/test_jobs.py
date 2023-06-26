import urllib.parse

import pytest

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


@pytest.fixture
def single_job():
    return {
        "jobs": [
            {
                "processID": "action_1",
                "type": "process",
                "jobID": "2595f2da-81a6-423c-84db-935e6791046e",
                "status": "successful",
                "updated": "2023-04-28T15:49:03+00:00",
            }
        ],
        "links": [
            {
                "href": "http://www.example.com",
            }
        ],
    }


@pytest.fixture
def no_jobs():
    return {
        "jobs": [],
        "links": [
            {
                "href": "http://www.example.com",
            }
        ],
    }


@pytest.fixture
def all_jobs():
    return {
        "jobs": [
            {
                "processID": "action_2",
                "type": "process",
                "jobID": "81842304-0aa9-4609-89f0-1c86819b0752",
                "status": "accepted",
                "updated": "2023-04-28T15:49:00+00:00",
            },
            {
                "processID": "action_1",
                "type": "process",
                "jobID": "2595f2da-81a6-423c-84db-935e6791046e",
                "status": "successful",
                "updated": "2023-04-28T15:49:03+00:00",
            },
        ],
        "links": [
            {
                "href": "http://www.example.com",
            }
        ],
    }


@pytest.mark.asyncio
async def test_get_all_jobs(test_client, all_jobs):
    response = test_client.get("/jobs")
    assert response.status_code == 200
    assert response.json() == all_jobs


@pytest.mark.asyncio
async def test_get_single_job(test_client, single_job):
    response = test_client.get(
        "/jobs?limit=1&processID=action_1&parentID=cf8ff7f0-ce5d-4de6-8026-4e551787385f"
    )
    assert response.status_code == 200
    assert response.json() == single_job


@pytest.mark.asyncio
async def test_get_all_jobs_start(test_client, all_jobs):
    response = test_client.get(
        "/jobs?"
        + urllib.parse.urlencode({"startDatetime": "2023-04-28T15:49:00+00:00"})
    )
    assert response.status_code == 200
    assert response.json() == all_jobs


@pytest.mark.asyncio
async def test_get_no_job_start(test_client, no_jobs):
    response = test_client.get(
        "/jobs?"
        + urllib.parse.urlencode({"startDatetime": "2023-04-29T15:49:00+00:00"})
    )
    assert response.status_code == 200
    assert response.json() == no_jobs


@pytest.mark.asyncio
async def test_get_no_job_end(test_client, no_jobs):
    response = test_client.get(
        "/jobs?" + urllib.parse.urlencode({"endDatetime": "2023-04-27T15:49:00+00:00"})
    )
    assert response.status_code == 200
    assert response.json() == no_jobs


@pytest.mark.asyncio
async def test_get_job_by_process(test_client, single_job):
    response = test_client.get("/jobs?processID=action_1")
    assert response.status_code == 200
    assert response.json() == single_job


@pytest.mark.asyncio
async def test_get_job_by_job_id(test_client, single_job):
    response = test_client.get("/jobs/2595f2da-81a6-423c-84db-935e6791046e")
    assert response.status_code == 200
    assert response.json() == single_job["jobs"][0]


@pytest.mark.asyncio
async def test_get_job_by_job_id_404(test_client):
    response = test_client.get("/jobs/00000000-1111-2222-3333-444444444444/results")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_job_results(test_client):
    response = test_client.get("/jobs/2595f2da-81a6-423c-84db-935e6791046e/results")
    assert response.status_code == 200
    assert response.json() == {
        "process_id": "2595f2da-81a6-423c-84db-935e6791046e",
        "payload": "test_output",
    }


@pytest.mark.asyncio
async def test_get_job_results_404(test_client):
    response = test_client.get("/jobs/00000000-1111-2222-3333-444444444444/results")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_job_payload(test_client):
    response = test_client.get("/jobs/2595f2da-81a6-423c-84db-935e6791046e/payload")
    assert response.status_code == 200
    assert response.json() == {
        "process_id": "2595f2da-81a6-423c-84db-935e6791046e",
        "payload": "test_input",
    }


@pytest.mark.asyncio
async def test_get_job_payload_404(test_client):
    response = test_client.get("/jobs/00000000-1111-2222-3333-444444444444/payload")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_job_status(test_client, single_job):
    response = test_client.get("/jobs/2595f2da-81a6-423c-84db-935e6791046e")
    assert response.status_code == 200
    assert response.json() == single_job["jobs"][0]


@pytest.mark.asyncio
async def test_get_job_status_404(test_client):
    response = test_client.get("/jobs/00000000-1111-2222-3333-444444444444")
    assert response.status_code == 404
