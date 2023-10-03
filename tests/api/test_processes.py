import asyncio
import json

import pytest
from fastapi.testclient import TestClient
from httpx import Response


def mirror_workflow(request_endpoint: str):
    return {
        "processes": [
            {
                "title": "mirror",
                "description": "A workflow to copy STAC items into a local mirror",
                "id": "mirror",
                "version": "2",
                "jobControlOptions": ["async-execute"],
                "handlerType": "argoWorkflow",
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


def mirror_workflow_process(request_endpoint: str):
    mirror = mirror_workflow(request_endpoint)["processes"][0]
    mirror.update(
        {
            "cacheKeyHashIncludes": [".features[].id", ".features[].collection"],
            "cacheKeyHashExcludes": [],
            "inputs": {
                "payload": {
                    "minOccurs": 1,
                    "maxOccurs": 1,
                    "schema": {
                        "$ref": "http://testserver/processes/mirror/inputsschema",
                    },
                },
            },
            "outputs": {
                "payload": {
                    "schema": {
                        "$ref": "http://testserver/processes/mirror/outputsschema",
                    },
                },
            },
        }
    )
    return mirror


def cirrus_workflow(request_endpoint: str):
    return {
        "processes": [
            {
                "title": "Cirrus example workflow",
                "description": "An example workflow config for a cirrus workflow",
                "id": "cirrus-example",
                "version": "1",
                "jobControlOptions": ["async-execute"],
                "handlerType": "cirrusWorkflow",
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
            {
                "href": f"http://testserver{request_endpoint}&lastID=cirrus-example",
                "rel": "next",
                "type": "application/json",
            },
        ],
    }


def all_processes(request_endpoint: str):
    return {
        "processes": [
            {
                "title": "Cirrus example workflow",
                "description": "An example workflow config for a cirrus workflow",
                "id": "cirrus-example",
                "version": "1",
                "jobControlOptions": ["async-execute"],
                "handlerType": "cirrusWorkflow",
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
            {
                "title": "mirror",
                "description": "A workflow to copy STAC items into a local mirror",
                "id": "mirror",
                "version": "2",
                "jobControlOptions": ["async-execute"],
                "handlerType": "argoWorkflow",
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


def all_processes_reorder(request_endpoint: str):
    return {
        "processes": [
            {
                "title": "mirror",
                "description": "A workflow to copy STAC items into a local mirror",
                "id": "mirror",
                "version": "2",
                "jobControlOptions": ["async-execute"],
                "handlerType": "argoWorkflow",
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
                "handlerType": "cirrusWorkflow",
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


process_payload_valid = {
    "inputs": {
        "payload": {
            "value": {
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
            },
        },
    },
    "response": "document",
}


process_payload_cache_key_change = {
    "inputs": {
        "payload": {
            "value": {
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
    },
    "response": "document",
}


process_payload_invalid = {
    "inputs": {
        "payload": {
            "value": {
                "type": "FeatureCollection",
                "features": [{"id": "string", "collection": {"a": 122}}],
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
    },
    "response": "document",
}


process_payload_valid_wf_name_not_in_config = {
    "inputs": {
        "payload": {
            "value": {
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
    },
    "response": "document",
}


@pytest.mark.asyncio
async def test_get_all_processes(test_client: TestClient) -> None:
    url: str = "/processes"
    response: Response = test_client.get(url)
    assert response.status_code == 200
    assert response.json() == all_processes(url)


@pytest.mark.asyncio
async def test_get_all_processes_handler(test_client: TestClient) -> None:
    url: str = "/processes?handler=argoHandler"
    response: Response = test_client.get(url)
    assert response.status_code == 200
    assert response.json() == mirror_workflow(url)


@pytest.mark.asyncio
async def test_get_all_processes_handler_multiple(test_client: TestClient) -> None:
    url: str = "/processes?handler=argoHandler&handler=cirrusHandler"
    response: Response = test_client.get(url)
    assert response.status_code == 200
    assert response.json() == all_processes_reorder(url)


@pytest.mark.asyncio
async def test_get_all_processes_limit(test_client: TestClient) -> None:
    url: str = "/processes?limit=1"
    response: Response = test_client.get(url)
    assert response.status_code == 200
    assert response.json() == cirrus_workflow(url)


@pytest.mark.asyncio
async def test_get_all_processes_type(test_client: TestClient) -> None:
    url: str = "/processes?type=argoWorkflow"
    response: Response = test_client.get(url)
    assert response.status_code == 200
    assert response.json() == mirror_workflow(url)


@pytest.mark.asyncio
async def test_get_all_processes_type_multiple(test_client: TestClient) -> None:
    url: str = "/processes?type=argoWorkflow&type=cirrusWorkflow"
    response: Response = test_client.get(url)
    assert response.status_code == 200
    assert response.json() == all_processes_reorder(url)


@pytest.mark.asyncio
async def test_get_all_processes_limit_handler(test_client: TestClient) -> None:
    url: str = "/processes?limit=2&handler=argoHandler"
    response: Response = test_client.get(url)
    assert response.status_code == 200
    assert response.json() == mirror_workflow(url)


@pytest.mark.asyncio
async def test_get_all_processes_limit_type(test_client: TestClient) -> None:
    url: str = "/processes?limit=2&type=argoWorkflow"
    response: Response = test_client.get(url)
    assert response.status_code == 200
    assert response.json() == mirror_workflow(url)


@pytest.mark.asyncio
async def test_get_all_processes_handler_type(test_client: TestClient) -> None:
    url: str = "/processes?handler=argoHandler&type=argoWorkflow"
    response: Response = test_client.get(url)
    assert response.status_code == 200
    assert response.json() == mirror_workflow(url)


@pytest.mark.asyncio
async def test_get_all_processes_invalid_type(test_client: TestClient) -> None:
    response: Response = test_client.get("/processes?type=invalid_type")
    assert response.status_code == 200
    assert response.json()["processes"] == []


@pytest.mark.asyncio
async def test_get_process_by_process_id(test_client: TestClient) -> None:
    url: str = "/processes/mirror"
    response: Response = test_client.get(url)
    assert response.status_code == 200
    print(response.json())
    assert response.json() == mirror_workflow_process(url)


@pytest.mark.asyncio
async def test_get_process_by_process_id_404(test_client: TestClient) -> None:
    response: Response = test_client.get("/processes/mirror-test")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_post_valid_id_valid_payload(test_client: TestClient) -> None:
    response: Response = test_client.post(
        "/processes/cirrus-example/execution",
        content=json.dumps(process_payload_valid),
    )
    print(response.json())
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_post_no_inputs(test_client: TestClient) -> None:
    response: Response = test_client.post(
        "/processes/mirror/execution",
        content="{}",
    )
    assert response.status_code == 422


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
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Not Found",
        "status": 404,
        "type": "http://www.opengis.net/def/exceptions/ogcapi-processes-1/1.0/no-such-process",
    }


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
    payload = json.dumps(process_payload_valid)
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(post_payload_cache(test_client, payload))
        task2 = tg.create_task(post_payload_cache(test_client, payload))
    res1 = task1.result()
    res2 = task2.result()
    print(res1.content)
    print(res2)
    assert task1.result().status_code == 201
    assert task2.result().status_code == 303


@pytest.mark.asyncio
async def test_post_execution_no_features(test_client: TestClient) -> None:
    payload = {
        "inputs": {
            "payload": {
                "value": {
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
                            "tasks": {},
                        }
                    ],
                }
            }
        },
        "response": "document",
    }
    result = await post_payload_cache(test_client, json.dumps(payload))
    assert result.status_code == 422
    assert result.json() == {
        "status": 422,
        "detail": "'features' is a required property",
        "path": "$.payload.value",
    }


@pytest.mark.asyncio
async def test_post_execution_empty_features(test_client: TestClient) -> None:
    payload = {
        "inputs": {
            "payload": {
                "value": {
                    "features": [],
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
            }
        },
        "response": "document",
    }
    result = await post_payload_cache(test_client, json.dumps(payload))
    assert result.status_code == 422
    assert result.json() == {
        "status": 422,
        "detail": "[] is too short",
        "path": "$.payload.value.features",
    }


@pytest.mark.asyncio
async def test_post_execution_no_collections(test_client: TestClient) -> None:
    payload = {
        "inputs": {
            "payload": {
                "value": {
                    "features": [{"id": "string", "collection": "string"}],
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
            }
        },
        "response": "document",
    }
    result = await post_payload_cache(test_client, json.dumps(payload))
    assert result.status_code == 422
    assert result.json() == {
        "status": 422,
        "detail": "{} does not have enough properties",
        "path": "$.payload.value.process[0].upload_options.collections",
    }


@pytest.mark.asyncio
async def test_post_execution_chaining(test_client: TestClient) -> None:
    payload = {
        "inputs": {
            "payload": {
                "value": {
                    "type": "FeatureCollection",
                    "features": [
                        {
                            "id": "item",
                            "collection": None,
                        },
                    ],
                    "process": [
                        {
                            "description": "first workflow",
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
                                "description": "chained workflow",
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
            }
        },
        "response": "document",
    }
    result = await post_payload_cache(test_client, json.dumps(payload))
    assert result.status_code == 201


@pytest.mark.asyncio
async def test_post_execution_bad_chain(test_client: TestClient) -> None:
    payload = {
        "inputs": {
            "payload": {
                "value": {
                    "type": "FeatureCollection",
                    "features": [
                        {
                            "id": "item",
                            "collection": "unique-value-352352355",
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
            }
        },
        "response": "document",
    }
    result = await post_payload_cache(test_client, json.dumps(payload))
    assert result.status_code == 422
    assert result.json() == {
        "status": 422,
        "detail": "[{'tasks': {}, 'description': 'string', 'upload_options': {'path_template': 'string', 'collections': {'my-collection': '.*'}, 'public_assets': [], 'headers': {}, 's3_urls': True}, 'workflow': 'mirror'}] is not of type 'object'",
        "path": "$.payload.value.process[0]",
    }


@pytest.mark.asyncio
async def test_get_inputsschema(test_client: TestClient) -> None:
    url: str = "/processes/mirror/inputsschema"
    response: Response = test_client.get(url)
    assert response.status_code == 200
    assert response.headers.get("content-type") == "application/schema+json"
    assert response.json() == {
        "type": "object",
        "properties": {
            "payload": {
                "type": "object",
                "properties": {
                    "value": {
                        "type": "object",
                        "properties": {
                            "features": {
                                "items": {"$ref": "#/$defs/feature"},
                                "minItems": 1,
                                "maxItems": 1,
                                "type": "array",
                                "uniqueItems": True,
                            },
                            "id": {"type": "string"},
                            "process": {"$ref": "#/$defs/workflows"},
                            "type": {
                                "type": "string",
                                "pattern": "^FeatureCollection$",
                            },
                        },
                        "required": ["type", "features", "process"],
                    }
                },
                "required": ["value"],
            }
        },
        "required": ["payload"],
        "$defs": {
            "feature": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "collection": {"type": ["string", "null"]},
                },
                "required": ["id", "collection"],
            },
            "tasks": {"type": "object"},
            "upload_options": {
                "properties": {
                    "collections": {
                        "additionalProperties": {"type": "string"},
                        "minProperties": 1,
                        "type": "object",
                    },
                    "path_template": {"type": "string"},
                },
                "type": "object",
            },
            "workflow": {
                "properties": {
                    "description": {"type": "string"},
                    "replace": {"type": "boolean"},
                    "tasks": {"$ref": "#/$defs/tasks"},
                    "upload_options": {"$ref": "#/$defs/upload_options"},
                    "workflow": {"type": "string", "pattern": "^mirror$"},
                },
                "required": ["workflow", "upload_options"],
                "type": "object",
            },
            "workflows": {
                "prefixItems": [{"$ref": "#/$defs/workflow"}],
                "additionalItems": {
                    "type": [
                        {"$ref": "#/$defs/workflow"},
                        {
                            "items": {"$ref": "#/$defs/workflow"},
                            "type": "array",
                            "uniqueItems": True,
                            "minItems": 1,
                        },
                    ]
                },
                "minItems": 1,
                "type": "array",
                "uniqueItems": True,
            },
        },
        "$schema": "http://testserver/processes/mirror/inputsschema",
    }


@pytest.mark.asyncio
async def test_get_inputsschema_not_found(test_client: TestClient) -> None:
    url: str = "/processes/badworkflowname/inputsschema"
    response: Response = test_client.get(url)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_outputsschema(test_client: TestClient) -> None:
    url: str = "/processes/mirror/outputsschema"
    response: Response = test_client.get(url)
    assert response.status_code == 200
    assert response.headers.get("content-type") == "application/schema+json"
    assert response.json() == {
        "type": "object",
        "properties": {
            "payload": {
                "type": "object",
                "properties": {
                    "value": {
                        "type": "object",
                        "properties": {
                            "features": {
                                "items": {"$ref": "#/$defs/feature"},
                                "minItems": 1,
                                "maxItems": 1,
                                "type": "array",
                                "uniqueItems": True,
                            },
                            "id": {"type": "string"},
                            "process": {"$ref": "#/$defs/workflows"},
                            "type": {
                                "type": "string",
                                "pattern": "^FeatureCollection$",
                            },
                        },
                        "required": ["type", "features", "process"],
                    }
                },
                "required": ["value"],
            }
        },
        "required": ["payload"],
        "$defs": {
            "feature": {"type": "object"},
            "tasks": {"type": "object"},
            "upload_options": {
                "properties": {
                    "collections": {
                        "additionalProperties": {"type": "string"},
                        "type": "object",
                    },
                    "path_template": {"type": "string"},
                },
                "type": "object",
            },
            "workflow": {
                "properties": {
                    "description": {"type": "string"},
                    "replace": {"type": "boolean"},
                    "tasks": {"$ref": "#/$defs/tasks"},
                    "upload_options": {"$ref": "#/$defs/upload_options"},
                    "workflow": {"type": "string", "pattern": "^mirror$"},
                },
                "required": ["workflow", "upload_options"],
                "type": "object",
            },
            "workflows": {
                "prefixItems": [{"$ref": "#/$defs/workflow"}],
                "additionalItems": {
                    "type": [
                        {"$ref": "#/$defs/workflow"},
                        {
                            "items": {"$ref": "#/$defs/workflow"},
                            "type": "array",
                            "uniqueItems": True,
                            "minItems": 1,
                        },
                    ]
                },
                "minItems": 1,
                "type": "array",
                "uniqueItems": True,
            },
        },
        "$schema": "http://testserver/processes/mirror/outputsschema",
    }


@pytest.mark.asyncio
async def test_get_outputsschema_not_found(test_client: TestClient) -> None:
    url: str = "/processes/badworkflowname/outputsschema"
    response: Response = test_client.get(url)
    assert response.status_code == 404
