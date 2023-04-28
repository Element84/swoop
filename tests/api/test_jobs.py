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

        response = app_client.get('/jobs?limit=1&process_id=foo&collection_id=foo,bar')
        assert response.status_code == 200
        #assert number of records = 1

        # response = app_client.get('/jobs?process_id=foo')
        # assert response.status_code == 200
        # #assert number of records = 1

        # response = app_client.get('/jobs?collection_id=bar')
        # assert response.status_code == 200
        # #assert number of records = 1

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

        # response = app_client.get('/jobs?limit=1&process_id=x&collection_id=y&item_id=z&start_datetime=foo&end_datetime=bar&parent_id=123043')
        # assert response.status_code == 200
        # #assert number of records = 1

        # response = app_client.get('/jobs?item_id=foo,bar')
        # assert response.status_code == 200
        # #assert number of records = 2

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
