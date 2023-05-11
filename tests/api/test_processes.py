import pytest


@pytest.fixture
def single_process():
    return {
        "processes": [
            {
                "title": "mirror",
                "description": "A workflow to copy STAC items into a local mirror",
                "keywords": None,
                "metadata": None,
                "additionalParameters": None,
                "id": "mirror",
                "version": "2",
                "name": "mirror",
                "processID": "mirror",
                "jobControlOptions": ["async-execute"],
                "outputTransmission": None,
                "handler": "argo-workflow",
                "argoTemplate": "workflowtemplate/mirror-workflow",
                "cacheEnabled": True,
                "cacheKeyHashIncludes": ["features[*].properties.version"],
                "cacheKeyHashExcludes": [],
                "links": None,
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
def all_processes():
    return {
        "processes": [
            {
                "title": "mirror",
                "description": "A workflow to copy STAC items into a local mirror",
                "keywords": None,
                "metadata": None,
                "additionalParameters": None,
                "id": "mirror",
                "version": "2",
                "name": "mirror",
                "processID": "mirror",
                "jobControlOptions": ["async-execute"],
                "outputTransmission": None,
                "handler": "argo-workflow",
                "argoTemplate": "workflowtemplate/mirror-workflow",
                "cacheEnabled": True,
                "cacheKeyHashIncludes": ["features[*].properties.version"],
                "cacheKeyHashExcludes": [],
                "links": None,
            },
            {
                "title": "cirrus-example",
                "description": "An example workflow config for a cirrus workflow",
                "keywords": None,
                "metadata": None,
                "additionalParameters": None,
                "id": "cirrus-example",
                "version": "1",
                "name": "cirrus-example",
                "processID": "cirrus-example",
                "jobControlOptions": ["async-execute"],
                "outputTransmission": None,
                "handler": "cirrus-workflow",
                "argoTemplate": None,
                "cacheEnabled": False,
                "cacheKeyHashIncludes": None,
                "cacheKeyHashExcludes": None,
                "links": None,
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
def no_processes():
    return {
        "processes": [],
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
def mirror_workflow_process():
    return {
        "title": "mirror",
        "description": "A workflow to copy STAC items into a local mirror",
        "keywords": None,
        "metadata": None,
        "additionalParameters": None,
        "id": "mirror",
        "version": "2",
        "name": "mirror",
        "processID": "mirror",
        "jobControlOptions": ["async-execute"],
        "outputTransmission": None,
        "handler": "argo-workflow",
        "argoTemplate": "workflowtemplate/mirror-workflow",
        "cacheEnabled": True,
        "cacheKeyHashIncludes": ["features[*].properties.version"],
        "cacheKeyHashExcludes": [],
        "links": None,
        "inputs": None,
        "outputs": None,
    }


@pytest.mark.asyncio
async def test_get_all_processes(test_client, all_processes):
    response = test_client.get("/processes")
    assert response.status_code == 200
    assert response.json() == all_processes


@pytest.mark.asyncio
async def test_get_all_processes_limit_filter(test_client, single_process):
    response = test_client.get("/processes?limit=1&process_id=mirror")
    assert response.status_code == 200
    assert response.json() == single_process


@pytest.mark.asyncio
async def test_get_all_processes_filter(test_client, single_process):
    response = test_client.get("/processes?process_id=mirror")
    assert response.status_code == 200
    assert response.json() == single_process


@pytest.mark.asyncio
async def test_get_all_processes_limit(test_client, single_process):
    response = test_client.get("/processes?limit=1")
    assert response.status_code == 200
    assert response.json() == single_process


@pytest.mark.asyncio
async def test_get_all_processes_none(test_client, no_processes):
    response = test_client.get("/processes?version=3")
    assert response.status_code == 200
    assert response.json() == no_processes


@pytest.mark.asyncio
async def test_get_process_by_process_id(test_client, mirror_workflow_process):
    response = test_client.get("/processes/mirror")
    assert response.status_code == 200
    assert response.json() == mirror_workflow_process


@pytest.mark.asyncio
async def test_get_process_by_process_id_404(test_client):
    response = test_client.get("/processes/mirror-test")
    assert response.status_code == 404