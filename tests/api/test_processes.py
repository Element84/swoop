import json
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def workflow_config_cache_key_change(api_fixtures_path) -> Path:
    return api_fixtures_path.joinpath("workflow-config-cache-key-change.yml")


@pytest.fixture(scope="session")
def workflow_config_version_increment(api_fixtures_path) -> Path:
    return api_fixtures_path.joinpath("workflow-config-version-inc.yml")


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
                "cacheKeyHashIncludes": [".features[].id", ".features[].collection"],
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
                "cacheKeyHashIncludes": [".features[].id", ".features[].collection"],
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
                "cacheKeyHashIncludes": [".features[].id", ".features[].collection"],
                "cacheKeyHashExcludes": [],
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
        "cacheKeyHashIncludes": [".features[].id", ".features[].collection"],
        "cacheKeyHashExcludes": [],
        "links": None,
        "inputs": None,
        "outputs": None,
    }


@pytest.fixture
def process_payload_valid():
    return {
        "inputs": {
            "payload": {
                "type": "FeatureCollection",
                "features": [
                    {
                        "id": "string",
                        "collection": "string",
                        "properties": {"version": 2},
                    }
                ],
                "process": [
                    {
                        "description": "string",
                        "tasks": {},
                        "upload_options": {
                            "path_template": "string",
                            "collections": {},
                            "public_assets": [],
                            "headers": {},
                            "s3_urls": True,
                        },
                        "workflow": "mirror",
                    }
                ],
            }
        },
        "response": "document",
    }


@pytest.fixture
def process_payload_invalid():
    return {
        "inputs": {
            "payload": {
                "type": "FeatureCollection",
                "features": [{"id": "string", "collection": 250}],
                "process": [
                    {
                        "description": "string",
                        "tasks": {},
                        "upload_options": {
                            "path_template": "string",
                            "collections": {},
                            "public_assets": [],
                            "headers": {},
                            "s3_urls": True,
                        },
                        "workflow": "mirror",
                    }
                ],
            }
        },
        "response": "document",
    }


@pytest.fixture
def process_payload_valid_wf_name_not_in_config():
    return {
        "inputs": {
            "payload": {
                "type": "FeatureCollection",
                "features": [{"id": "string", "collection": "string"}],
                "process": [
                    {
                        "description": "string",
                        "tasks": {},
                        "upload_options": {
                            "path_template": "string",
                            "collections": {},
                            "public_assets": [],
                            "headers": {},
                            "s3_urls": True,
                        },
                        "workflow": "hello",
                    }
                ],
            }
        },
        "response": "document",
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


@pytest.mark.asyncio
async def test_post_valid_id_valid_payload(test_client, process_payload_valid):
    response = test_client.post(
        "/processes/mirror/execution", data=json.dumps(process_payload_valid)
    )
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_post_valid_id_invalid_payload(test_client, process_payload_invalid):
    response = test_client.post(
        "/processes/mirror/execution", data=json.dumps(process_payload_invalid)
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_post_invalid_id_valid_payload(test_client, process_payload_valid):
    response = test_client.post(
        "/processes/invalid/execution", data=json.dumps(process_payload_valid)
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_post_process_id_not_found_in_config(
    test_client, process_payload_valid_wf_name_not_in_config
):
    response = test_client.post(
        "/processes/hello/execution",
        data=json.dumps(process_payload_valid_wf_name_not_in_config),
    )
    assert response.status_code == 404
