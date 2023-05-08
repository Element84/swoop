from fastapi.testclient import TestClient
import pytest
import urllib.parse


@pytest.fixture
def single_job():
    return {
        "jobs": [
            {
                "processID": "action_1",
                "type": "process",
                "jobID": "2595f2da-81a6-423c-84db-935e6791046e",
                "status": "successful",
                "message": None,
                "created": None,
                "started": None,
                "finished": None,
                "updated": "2023-04-28T15:49:03+00:00",
                "progress": None,
                "links": None,
                "parentID": "5001",
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
def same_jobs():
    return {
        "jobs": [
            {
                "processID": "action_1",
                "type": "process",
                "jobID": "2595f2da-81a6-423c-84db-935e6791046e",
                "status": "successful",
                "message": None,
                "created": None,
                "started": None,
                "finished": None,
                "updated": "2023-04-28T15:49:03+00:00",
                "progress": None,
                "links": None,
                "parentID": "5001",
            },
            {
                "processID": "action_1",
                "type": "process",
                "jobID": "2595f2da-81a6-423c-84db-935e6791046e",
                "status": "successful",
                "message": None,
                "created": None,
                "started": None,
                "finished": None,
                "updated": "2023-04-28T15:49:03+00:00",
                "progress": None,
                "links": None,
                "parentID": "5001",
            },
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
def no_jobs():
    return {
        "jobs": [],
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
def all_jobs():
    # TODO - figure out why 'action_1' is returned twice
    return {
        "jobs": [
            {
                "processID": "action_2",
                "type": "process",
                "jobID": "81842304-0aa9-4609-89f0-1c86819b0752",
                "status": "accepted",
                "message": None,
                "created": None,
                "started": None,
                "finished": None,
                "updated": "2023-04-28T15:49:00+00:00",
                "progress": None,
                "links": None,
                "parentID": "5002",
            },
            {
                "processID": "action_2",
                "type": "process",
                "jobID": "81842304-0aa9-4609-89f0-1c86819b0752",
                "status": "accepted",
                "message": None,
                "created": None,
                "started": None,
                "finished": None,
                "updated": "2023-04-28T15:49:00+00:00",
                "progress": None,
                "links": None,
                "parentID": "5002",
            },
            {
                "processID": "action_1",
                "type": "process",
                "jobID": "2595f2da-81a6-423c-84db-935e6791046e",
                "status": "successful",
                "message": None,
                "created": None,
                "started": None,
                "finished": None,
                "updated": "2023-04-28T15:49:03+00:00",
                "progress": None,
                "links": None,
                "parentID": "5001",
            },
            {
                "processID": "action_1",
                "type": "process",
                "jobID": "2595f2da-81a6-423c-84db-935e6791046e",
                "status": "successful",
                "message": None,
                "created": None,
                "started": None,
                "finished": None,
                "updated": "2023-04-28T15:49:03+00:00",
                "progress": None,
                "links": None,
                "parentID": "5001",
            },
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


@pytest.mark.asyncio
async def test_get_all_jobs(test_app, single_job, same_jobs, no_jobs, all_jobs):
    with TestClient(test_app) as app_client:
        response = app_client.get("/jobs")
        assert response.status_code == 200
        assert response.json() == all_jobs

        response = app_client.get("/jobs?limit=1&process_id=action_1&parent_id=5001")
        assert response.status_code == 200
        assert response.json() == single_job

        response = app_client.get("/jobs?process_id=action_1")
        assert response.status_code == 200
        assert response.json() == same_jobs

        response = app_client.get(
            "/jobs?"
            + urllib.parse.urlencode({"start_datetime": "2023-04-28T15:49:00+00:00"})
        )
        assert response.status_code == 200
        assert response.json() == all_jobs

        response = app_client.get(
            "/jobs?"
            + urllib.parse.urlencode({"start_datetime": "2023-04-29T15:49:00+00:00"})
        )
        assert response.status_code == 200
        assert response.json() == no_jobs

        response = app_client.get(
            "/jobs?"
            + urllib.parse.urlencode({"end_datetime": "2023-04-27T15:49:00+00:00"})
        )
        assert response.status_code == 200
        assert response.json() == no_jobs

        response = app_client.get("/jobs?parent_id=5001")
        assert response.status_code == 200
        assert response.json() == same_jobs


@pytest.mark.asyncio
async def test_get_job_by_job_id(test_app, single_job):
    with TestClient(test_app) as app_client:
        response = app_client.get("/jobs/2595f2da-81a6-423c-84db-935e6791046e")
        assert response.status_code == 200
        assert response.json() == single_job["jobs"][0]

        response = app_client.get("/jobs/00000000-1111-2222-3333-444444444444/results")
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_job_results(test_app):
    with TestClient(test_app) as app_client:
        response = app_client.get("/jobs/2595f2da-81a6-423c-84db-935e6791046e/results")
        assert response.status_code == 200
        assert response.json() == {"example": "example results"}

        response = app_client.get("/jobs/00000000-1111-2222-3333-444444444444/results")
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_job_payload(test_app):
    with TestClient(test_app) as app_client:
        response = app_client.get("/jobs/2595f2da-81a6-423c-84db-935e6791046e/payload")
        assert response.status_code == 200
        assert response.json() == {"example": "example payload"}

        response = app_client.get("/jobs/00000000-1111-2222-3333-444444444444/payload")
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_job_status(test_app, single_job):
    with TestClient(test_app) as app_client:
        response = app_client.get("/jobs/2595f2da-81a6-423c-84db-935e6791046e")
        assert response.status_code == 200
        assert response.json() == single_job["jobs"][0]

        response = app_client.get("/jobs/00000000-1111-2222-3333-444444444444")
        assert response.status_code == 404
