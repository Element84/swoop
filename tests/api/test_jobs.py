from fastapi.testclient import TestClient
import pytest
import json


@pytest.mark.asyncio
async def test_get_all_jobs(test_app):
    with TestClient(test_app) as app_client:

        response = app_client.get('/jobs/test')
        assert response.status_code == 200
        assert '2595f2da-81a6-423c-84db-935e6791046e' in json.dumps(response.json())


