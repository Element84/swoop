import asyncio
import json

import pytest
from fastapi.testclient import TestClient
from httpx import Response


def single_process(request_endpoint: str):
    return {
        "processes": [
            {
                "title": "mirror",
                "description": "A workflow to copy STAC items into a local mirror",
                "id": "mirror",
                "version": "2",
                "jobControlOptions": ["async-execute"],
                "handler_type": "argo-workflow",
                "links": [
                    {
                        "href": "http://testserver/",
                        "rel": "root",
                        "type": "application/json",
                    },
                    {
                        "href": "http://testserver/processes/mirror",
                        "rel": "self",
                        "type": "application/json",
                    },
                ],
            },
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


def all_processes(request_endpoint: str):
    return {
        "processes": [
            {
                "title": "mirror",
                "description": "A workflow to copy STAC items into a local mirror",
                "id": "mirror",
                "version": "2",
                "jobControlOptions": ["async-execute"],
                "handler_type": "argo-workflow",
                "links": [
                    {
                        "href": "http://testserver/",
                        "rel": "root",
                        "type": "application/json",
                    },
                    {
                        "href": "http://testserver/processes/mirror",
                        "rel": "self",
                        "type": "application/json",
                    },
                ],
            },
            {
                "title": "Cirrus example workflow",
                "description": "An example workflow config for a cirrus workflow",
                "id": "cirrus-example",
                "version": "1",
                "jobControlOptions": ["async-execute"],
                "handler_type": "cirrus-workflow",
                "links": [
                    {
                        "href": "https://example.com/repo",
                        "rel": "external",
                        "type": "text/html",
                        "title": "source repository",
                    },
                    {
                        "href": "https://example.com/docs",
                        "rel": "external",
                        "type": "text/html",
                        "title": "process documentation",
                    },
                    {
                        "href": "http://testserver/",
                        "rel": "root",
                        "type": "application/json",
                    },
                    {
                        "href": "http://testserver/processes/cirrus-example",
                        "rel": "self",
                        "type": "application/json",
                    },
                ],
            },
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


mirror_workflow_process = {
    "title": "mirror",
    "description": "A workflow to copy STAC items into a local mirror",
    "id": "mirror",
    "version": "2",
    "jobControlOptions": ["async-execute"],
    "handler_type": "argo-workflow",
    "cacheKeyHashIncludes": [".features[].id", ".features[].collection"],
    "cacheKeyHashExcludes": [],
    "links": [
        {
            "href": "http://testserver/",
            "rel": "root",
            "type": "application/json",
        },
        {
            "href": "http://testserver/processes/mirror",
            "rel": "self",
            "type": "application/json",
        },
    ],
}


process_payload_valid = {
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
                        "collections": {"my-collection": ".*"},
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


process_payload_cache = {
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
                        "collections": {"my-collection": ".*"},
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


process_payload_cache_key_change = {
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
                        "collections": {"my-collection": ".*"},
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


process_payload_invalid = {
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
                        "collections": {"my-collection": ".*"},
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


process_payload_valid_wf_name_not_in_config = {
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
                        "collections": {"my-collection": ".*"},
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
async def test_get_all_processes(test_client: TestClient) -> None:
    url: str = "/processes/"
    response: Response = test_client.get(url)
    assert response.status_code == 200
    assert response.json() == all_processes(url)


@pytest.mark.asyncio
async def test_get_all_processes_handler(test_client: TestClient) -> None:
    url: str = "/processes/?handler=argo-handler"
    response: Response = test_client.get(url)
    assert response.status_code == 200
    assert response.json() == single_process(url)


@pytest.mark.asyncio
async def test_get_all_processes_handler_multiple(test_client: TestClient) -> None:
    url: str = "/processes/?handler=argo-handler&handler=cirrus-handler"
    response: Response = test_client.get(url)
    assert response.status_code == 200
    assert response.json() == all_processes(url)


@pytest.mark.asyncio
async def test_get_all_processes_limit(test_client: TestClient) -> None:
    url: str = "/processes/?limit=1"
    response: Response = test_client.get(url)
    assert response.status_code == 200
    assert response.json() == single_process(url)


@pytest.mark.asyncio
async def test_get_all_processes_type(test_client: TestClient) -> None:
    url: str = "/processes/?type=argo-workflow"
    response: Response = test_client.get(url)
    assert response.status_code == 200
    assert response.json() == single_process(url)


@pytest.mark.asyncio
async def test_get_all_processes_type_multiple(test_client: TestClient) -> None:
    url: str = "/processes/?type=argo-workflow&type=cirrus-workflow"
    response: Response = test_client.get(url)
    assert response.status_code == 200
    assert response.json() == all_processes(url)


@pytest.mark.asyncio
async def test_get_all_processes_limit_handler(test_client: TestClient) -> None:
    url: str = "/processes/?limit=2&handler=argo-handler"
    response: Response = test_client.get(url)
    assert response.status_code == 200
    assert response.json() == single_process(url)


@pytest.mark.asyncio
async def test_get_all_processes_limit_type(test_client: TestClient) -> None:
    url: str = "/processes/?limit=2&type=argo-workflow"
    response: Response = test_client.get(url)
    assert response.status_code == 200
    assert response.json() == single_process(url)


@pytest.mark.asyncio
async def test_get_all_processes_handler_type(test_client: TestClient) -> None:
    url: str = "/processes/?handler=argo-handler&type=argo-workflow"
    response: Response = test_client.get(url)
    assert response.status_code == 200
    assert response.json() == single_process(url)


@pytest.mark.asyncio
async def test_get_all_processes_invalid_type(test_client: TestClient) -> None:
    response: Response = test_client.get("/processes/?type=invalid_type")
    assert response.status_code == 200
    assert response.json()["processes"] == []


@pytest.mark.asyncio
async def test_get_process_by_process_id(test_client: TestClient) -> None:
    response: Response = test_client.get("/processes/mirror")
    assert response.status_code == 200
    assert response.json() == mirror_workflow_process


@pytest.mark.asyncio
async def test_get_process_by_process_id_404(test_client: TestClient) -> None:
    response: Response = test_client.get("/processes/mirror-test")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_post_valid_id_valid_payload(test_client: TestClient) -> None:
    response: Response = test_client.post(
        "/processes/mirror/execution",
        content=json.dumps(process_payload_valid),
    )
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_post_valid_id_invalid_payload(test_client: TestClient) -> None:
    response: Response = test_client.post(
        "/processes/mirror/execution",
        content=json.dumps(process_payload_invalid),
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_post_invalid_id_valid_payload(test_client: TestClient) -> None:
    response: Response = test_client.post(
        "/processes/invalid/execution",
        content=json.dumps(process_payload_valid),
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_post_process_id_not_found_in_config(test_client: TestClient) -> None:
    response: Response = test_client.post(
        "/processes/hello/execution",
        content=json.dumps(process_payload_valid_wf_name_not_in_config),
    )
    assert response.status_code == 404


async def post_payload_cache(test_client: TestClient, payload: str) -> Response:
    response: Response = test_client.post(
        "/processes/mirror/execution",
        content=payload,
        follow_redirects=False,
    )
    return response


@pytest.mark.asyncio
async def test_post_payload_cache_main(test_client: TestClient) -> None:
    payload = json.dumps(process_payload_cache)
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(post_payload_cache(test_client, payload))
        task2 = tg.create_task(post_payload_cache(test_client, payload))
    assert task1.result().status_code == 201
    assert task2.result().status_code == 303


@pytest.mark.asyncio
async def test_post_execution_no_features(test_client: TestClient) -> None:
    payload = {
        "inputs": {
            "payload": {
                "type": "FeatureCollection",
                "process": [
                    {
                        "description": "string",
                        "upload_options": {
                            "path_template": "string",
                            "collections": {"my-collection": ".*"},
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
    result = await post_payload_cache(test_client, json.dumps(payload))
    assert result.status_code == 201

    uuid = result.json()["jobID"]
    _payload = test_client.app.state.io.get_object(f"executions/{uuid}/input.json")
    assert _payload.pop("features") == []
    assert _payload["process"][0].pop("tasks") == {}
    assert _payload == payload["inputs"]["payload"]


@pytest.mark.asyncio
async def test_post_execution_no_collections(test_client: TestClient) -> None:
    payload = {
        "inputs": {
            "payload": {
                "type": "FeatureCollection",
                "process": [
                    {
                        "description": "string",
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
    result = await post_payload_cache(test_client, json.dumps(payload))
    assert result.status_code == 422
    assert result.json() == {
        "detail": [
            {
                "loc": [
                    "body",
                    "inputs",
                    "payload",
                    "process",
                    0,
                    "upload_options",
                    "collections",
                ],
                "msg": "Collections must contain at least one item in the map",
                "type": "value_error",
            },
            {
                "loc": ["body", "inputs", "payload", "process", 0],
                "msg": "value is not a valid list",
                "type": "type_error.list",
            },
        ],
    }


@pytest.mark.asyncio
async def test_post_execution_chaining(test_client: TestClient) -> None:
    payload = {
        "inputs": {
            "payload": {
                "type": "FeatureCollection",
                "features": [
                    {
                        "id": "item",
                        "collection": None,
                    },
                ],
                "process": [
                    {
                        "description": "string",
                        "upload_options": {
                            "path_template": "string",
                            "collections": {"my-collection": ".*"},
                            "public_assets": [],
                            "headers": {},
                            "s3_urls": True,
                        },
                        "workflow": "mirror",
                    },
                    [
                        {
                            "tasks": {},
                            "description": "string",
                            "upload_options": {
                                "path_template": "string",
                                "collections": {"my-collection": ".*"},
                                "public_assets": [],
                                "headers": {},
                                "s3_urls": True,
                            },
                            "workflow": "mirror",
                        },
                    ],
                ],
            },
        },
        "response": "document",
    }
    result = await post_payload_cache(test_client, json.dumps(payload))
    assert result.status_code == 201

    uuid = result.json()["jobID"]
    _payload = test_client.app.state.io.get_object(f"executions/{uuid}/input.json")
    assert _payload["process"][0].pop("tasks") == {}
    assert _payload == payload["inputs"]["payload"]


@pytest.mark.asyncio
async def test_post_execution_bad_chain(test_client: TestClient) -> None:
    payload = {
        "inputs": {
            "payload": {
                "type": "FeatureCollection",
                "features": [
                    {
                        "id": "item",
                        "collection": None,
                    },
                ],
                "process": [
                    [
                        {
                            "tasks": {},
                            "description": "string",
                            "upload_options": {
                                "path_template": "string",
                                "collections": {"my-collection": ".*"},
                                "public_assets": [],
                                "headers": {},
                                "s3_urls": True,
                            },
                            "workflow": "mirror",
                        },
                    ],
                ],
            },
        },
        "response": "document",
    }
    result = await post_payload_cache(test_client, json.dumps(payload))
    assert result.status_code == 422
    assert result.json() == {
        "detail": [
            {
                "loc": ["body", "inputs", "payload", "process"],
                "msg": "first element in the `process` array cannot be an array",
                "type": "value_error",
            },
        ],
    }
