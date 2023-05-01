from fastapi.testclient import TestClient
import pytest


@pytest.mark.asyncio
async def test_get_all_jobs(test_app):
    with TestClient(test_app) as app_client:

        # response = app_client.get('/jobs?limit=7&parent_id=500,100&start_datetime=93202349&listy=foo,bar')
        # assert response.status_code == 200
        # assert '2595f2da-81a6-423c-84db-935e6791046e' in json.dumps(response.json())

        # response = app_client.get('/jobs')
        # assert response.status_code == 200
        # #assert number of records = all

        # TODO - change these values to real things on the fixture
        response = app_client.get('/jobs?limit=1&process_id=500&parent_id=101,102')
        assert response.status_code == 200
        #assert number of records = 1

        response = app_client.get('/jobs?process_id=action_name_1')
        assert response.status_code == 200
        #assert number of records = 1

        # response = app_client.get('/jobs?item_id=bar')
        # assert response.status_code == 200
        # #assert number of records = 1

        # response = app_client.get('/jobs?start_datetime=123043')
        # assert response.status_code == 200
        # #assert number of records = 1

        # response = app_client.get('/jobs?end_datetime=123043')
        # assert response.status_code == 200
        # #assert number of records = 1

        # response = app_client.get('/jobs?parent_id=123043')
        # assert response.status_code == 200
        # #assert number of records = 1

        # response = app_client.get('/jobs?limit=1&process_id=x&start_datetime=z&end_datetime=a&parent_id=b')
        # assert response.status_code == 200
        # #assert number of records = 1

        #assert False


@pytest.mark.asyncio
async def test_get_job_by_job_id(test_app):
    with TestClient(test_app) as app_client:
        response = app_client.get('/jobs/2595f2da-81a6-423c-84db-935e6791046e')
        assert response.status_code == 200
        assert response.json() == {
            'created': None,
            'finished': None,
            'jobID': 'jobid',
            'links': None,
            'message': None,
            'parentID': None,
            'processID': None,
            'progress': None,
            'started': None,
            'status': 'running',
            'type': 'process',
            'updated': None,
        }

        response = app_client.get('/jobs/00000000-1111-2222-3333-444444444444/results')
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_job_results(test_app):
    with TestClient(test_app) as app_client:
        # response = app_client.get('/jobs/2595f2da-81a6-423c-84db-935e6791046e/results')
        # assert response.status_code == 200
        # assert response.json() == {}

        response = app_client.get('/jobs/00000000-1111-2222-3333-444444444444/results')
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_job_payload(test_app):
    with TestClient(test_app) as app_client:
        response = app_client.get('/jobs/2595f2da-81a6-423c-84db-935e6791046e/payload')
        assert response.status_code == 200
        assert response.json() == {
            "example": "example payload"
        }

        response = app_client.get('/jobs/00000000-1111-2222-3333-444444444444/payload')
        assert response.status_code == 404
