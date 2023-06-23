import asyncio
import json

import pytest


@pytest.fixture
def single_process():
    return {
        "processes": [
            {
                "title": "mirror",
                "description": "A workflow to copy STAC items into a local mirror",
                "id": "mirror",
                "version": "2",
                "jobControlOptions": ["async-execute"],
                "type": "argo-workflow",
            }
        ],
        "links": [
            {
                "href": "http://www.example.com",
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
                "id": "mirror",
                "version": "2",
                "jobControlOptions": ["async-execute"],
                "type": "argo-workflow",
            },
            {
                "title": "cirrus-example",
                "description": "An example workflow config for a cirrus workflow",
                "id": "cirrus-example",
                "version": "1",
                "jobControlOptions": ["async-execute"],
                "type": "cirrus-workflow",
            },
        ],
        "links": [
            {
                "href": "http://www.example.com",
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
            }
        ],
    }


@pytest.fixture
def mirror_workflow_process():
    return {
        "title": "mirror",
        "description": "A workflow to copy STAC items into a local mirror",
        "id": "mirror",
        "version": "2",
        "jobControlOptions": ["async-execute"],
        "type": "argo-workflow",
        "cacheKeyHashIncludes": [".features[].id", ".features[].collection"],
        "cacheKeyHashExcludes": [],
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
def process_payload_cache():
    return {
        "inputs": {
            "payload": {
                "type": "FeatureCollection",
                "features": [
                    {
                        "id": "id1",
                        "collection": "coll1",
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
def process_payload_cache_key_change():
    return {
        "inputs": {
            "payload": {
                "type": "FeatureCollection",
                "features": [
                    {
                        "id": "id2",
                        "collection": "coll2",
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
async def test_get_all_processes_handler(test_client, single_process):
    response = test_client.get("/processes?handler=argo-handler")
    assert response.status_code == 200
    assert response.json() == single_process


@pytest.mark.asyncio
async def test_get_all_processes_limit(test_client, single_process):
    response = test_client.get("/processes?limit=1")
    assert response.status_code == 200
    assert response.json() == single_process


@pytest.mark.asyncio
async def test_get_all_processes_type(test_client, single_process):
    response = test_client.get("/processes?type=argo-workflow")
    assert response.status_code == 200
    assert response.json() == single_process


@pytest.mark.asyncio
async def test_get_all_processes_limit_handler(test_client, single_process):
    response = test_client.get("/processes?limit=2&handler=argo-handler")
    assert response.status_code == 200
    assert response.json() == single_process


@pytest.mark.asyncio
async def test_get_all_processes_limit_type(test_client, single_process):
    response = test_client.get("/processes?limit=2&type=argo-workflow")
    assert response.status_code == 200
    assert response.json() == single_process


@pytest.mark.asyncio
async def test_get_all_processes_handler_type(test_client, single_process):
    response = test_client.get("/processes?handler=argo-handler&type=argo-workflow")
    assert response.status_code == 200
    assert response.json() == single_process


@pytest.mark.asyncio
async def test_get_all_processes_invalid_type(test_client, no_processes):
    response = test_client.get("/processes?type=invalid_type")
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


async def post_payload_cache(test_client, process_payload_cache):
    response = test_client.post(
        "/processes/mirror/execution",
        data=json.dumps(process_payload_cache),
        follow_redirects=False,
    )
    return response


@pytest.mark.asyncio
async def test_post_payload_cache_main(test_client, process_payload_cache):
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(post_payload_cache(test_client, process_payload_cache))
        task2 = tg.create_task(post_payload_cache(test_client, process_payload_cache))
    assert task1.result().status_code == 201
    assert task2.result().status_code == 303
