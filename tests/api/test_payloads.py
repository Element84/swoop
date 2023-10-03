import json
from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from ..conftest import inject_database_fixture

inject_database_fixture(["base_01"], __name__)


a_payload = {
    "id": "ade69fe7-1d7d-572e-9f36-7242cc2aca77",
    "processID": "some_workflow",
    "invalidAfter": None,
    "links": [
        {
            "href": "http://testserver/",
            "rel": "root",
            "type": "application/json",
        },
        {
            "href": "http://testserver/cache/ade69fe7-1d7d-572e-9f36-7242cc2aca77",
            "rel": "self",
            "type": "application/json",
        },
    ],
}


a_payload_details = deepcopy(a_payload)
a_payload_details["links"].extend(
    [
        {
            "href": "http://testserver/jobs/0187c88d-a9e0-788c-adcb-c0b951f8be91",
            "rel": "job",
            "type": "application/json",
        },
        {
            "href": "http://testserver/jobs/0187c88d-a9e0-757e-aa36-2fbb6c834cb5",
            "rel": "job",
            "type": "application/json",
        },
    ]
)

payload_input_unknown = {
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
                        "workflow": "some_workflow",
                    }
                ],
            },
        },
    },
    "response": "document",
}

payload_input_missing = {
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

payload_input_valid = {
    "inputs": {
        "payload": {
            "value": {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "stac_version": "1.0.0-beta.2",
                        "stac_extensions": ["eo", "view", "proj"],
                        "id": "S2B_17HQD_20201103_0_L2A",
                        "bbox": [
                            -78.85549714480591,
                            -33.5090673116811,
                            -77.66654434530413,
                            -33.171471085391424,
                        ],
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [
                                [
                                    [-78.84720324626629, -33.5090673116811],
                                    [-78.85549714480591, -33.171471085391424],
                                    [-78.68855580607664, -33.20224951876674],
                                    [-78.68565102210097, -33.20281229571297],
                                    [-78.43490780996153, -33.25398334754271],
                                    [-78.12962160400237, -33.31843449933885],
                                    [-77.92995605454519, -33.36103653713505],
                                    [-77.66899441916789, -33.41891691608237],
                                    [-77.66654434530413, -33.482909622076725],
                                    [-78.84720324626629, -33.5090673116811],
                                ]
                            ],
                        },
                        "properties": {
                            "datetime": "2020-11-03T15:22:26Z",
                            "platform": "sentinel-2b",
                            "constellation": "sentinel-2",
                            "instruments": ["msi"],
                            "gsd": 10,
                            "view:off_nadir": 0,
                            "proj:epsg": 32717,
                            "sentinel:utm_zone": 17,
                            "sentinel:latitude_band": "H",
                            "sentinel:grid_square": "QD",
                            "sentinel:sequence": "0",
                            "sentinel:product_id": "S2B20201103T185442",
                            "sentinel:data_coverage": 20.61,
                            "eo:cloud_cover": 51.56,
                            "sentinel:valid_cloud_cover": True,
                            "created": "2020-11-11T00:00:00Z",
                            "updated": "2020-11-11T00:00:00Z",
                        },
                        "collection": "sentinel-s2-l2a",
                        "assets": {
                            "thumbnail": {
                                "title": "Thumbnail",
                                "type": "image/png",
                                "roles": ["thumbnail"],
                                "href": "https://test",
                            },
                            "overview": {
                                "title": "True color image",
                                "type": "image/jp2",
                                "roles": ["overview"],
                                "gsd": 10,
                                "eo:bands": [
                                    {
                                        "name": "B04",
                                        "common_name": "red",
                                        "center_wavelength": 0.6645,
                                        "full_width_half_max": 0.038,
                                    },
                                    {
                                        "name": "B03",
                                        "common_name": "green",
                                        "center_wavelength": 0.56,
                                        "full_width_half_max": 0.045,
                                    },
                                    {
                                        "name": "B02",
                                        "common_name": "blue",
                                        "center_wavelength": 0.4966,
                                        "full_width_half_max": 0.098,
                                    },
                                ],
                                "href": "s3://sentinel-s2-l2a",
                            },
                            "info": {
                                "title": "Original JSON metadata",
                                "type": "application/json",
                                "roles": ["metadata"],
                                "href": "https://test",
                            },
                            "metadata": {
                                "title": "Original XML metadata",
                                "type": "application/xml",
                                "roles": ["metadata"],
                                "href": "https://test",
                            },
                            "visual": {
                                "title": "True color image",
                                "type": "image/jp2",
                                "roles": ["overview"],
                                "gsd": 10,
                                "eo:bands": [
                                    {
                                        "name": "B04",
                                        "common_name": "red",
                                        "center_wavelength": 0.6645,
                                        "full_width_half_max": 0.038,
                                    },
                                    {
                                        "name": "B03",
                                        "common_name": "green",
                                        "center_wavelength": 0.56,
                                        "full_width_half_max": 0.045,
                                    },
                                    {
                                        "name": "B02",
                                        "common_name": "blue",
                                        "center_wavelength": 0.4966,
                                        "full_width_half_max": 0.098,
                                    },
                                ],
                                "href": "s3://sentinel-s2-l2a",
                            },
                            "visual_20m": {
                                "title": "True color image",
                                "type": "image/jp2",
                                "roles": ["overview"],
                                "gsd": 20,
                                "eo:bands": [
                                    {
                                        "name": "B04",
                                        "common_name": "red",
                                        "center_wavelength": 0.6645,
                                        "full_width_half_max": 0.038,
                                    },
                                    {
                                        "name": "B03",
                                        "common_name": "green",
                                        "center_wavelength": 0.56,
                                        "full_width_half_max": 0.045,
                                    },
                                    {
                                        "name": "B02",
                                        "common_name": "blue",
                                        "center_wavelength": 0.4966,
                                        "full_width_half_max": 0.098,
                                    },
                                ],
                                "href": "s3://sentinel-s2-l2a",
                            },
                            "visual_60m": {
                                "title": "True color image",
                                "type": "image/jp2",
                                "roles": ["overview"],
                                "gsd": 60,
                                "eo:bands": [
                                    {
                                        "name": "B04",
                                        "common_name": "red",
                                        "center_wavelength": 0.6645,
                                        "full_width_half_max": 0.038,
                                    },
                                    {
                                        "name": "B03",
                                        "common_name": "green",
                                        "center_wavelength": 0.56,
                                        "full_width_half_max": 0.045,
                                    },
                                    {
                                        "name": "B02",
                                        "common_name": "blue",
                                        "center_wavelength": 0.4966,
                                        "full_width_half_max": 0.098,
                                    },
                                ],
                                "href": "s3://sentinel-s2-l2a",
                            },
                            "B01": {
                                "title": "Band 1 (coastal)",
                                "type": "image/jp2",
                                "roles": ["data"],
                                "gsd": 60,
                                "eo:bands": [
                                    {
                                        "name": "B01",
                                        "common_name": "coastal",
                                        "center_wavelength": 0.4439,
                                        "full_width_half_max": 0.027,
                                    }
                                ],
                                "href": "s3://sentinel-s2-l2a",
                            },
                            "B02": {
                                "title": "Band 2 (blue)",
                                "type": "image/jp2",
                                "roles": ["data"],
                                "gsd": 10,
                                "eo:bands": [
                                    {
                                        "name": "B02",
                                        "common_name": "blue",
                                        "center_wavelength": 0.4966,
                                        "full_width_half_max": 0.098,
                                    }
                                ],
                                "href": "s3://sentinel-s2-l2a",
                            },
                            "B03": {
                                "title": "Band 3 (green)",
                                "type": "image/jp2",
                                "roles": ["data"],
                                "gsd": 10,
                                "eo:bands": [
                                    {
                                        "name": "B03",
                                        "common_name": "green",
                                        "center_wavelength": 0.56,
                                        "full_width_half_max": 0.045,
                                    }
                                ],
                                "href": "s3://sentinel-s2-l2a",
                            },
                            "B04": {
                                "title": "Band 4 (red)",
                                "type": "image/jp2",
                                "roles": ["data"],
                                "gsd": 10,
                                "eo:bands": [
                                    {
                                        "name": "B04",
                                        "common_name": "red",
                                        "center_wavelength": 0.6645,
                                        "full_width_half_max": 0.038,
                                    }
                                ],
                                "href": "s3://sentinel-s2-l2a",
                            },
                            "B05": {
                                "title": "Band 5",
                                "type": "image/jp2",
                                "roles": ["data"],
                                "gsd": 20,
                                "eo:bands": [
                                    {
                                        "name": "B05",
                                        "center_wavelength": 0.7039,
                                        "full_width_half_max": 0.019,
                                    }
                                ],
                                "href": "s3://sentinel-s2-l2a",
                            },
                            "B06": {
                                "title": "Band 6",
                                "type": "image/jp2",
                                "roles": ["data"],
                                "gsd": 20,
                                "eo:bands": [
                                    {
                                        "name": "B06",
                                        "center_wavelength": 0.7402,
                                        "full_width_half_max": 0.018,
                                    }
                                ],
                                "href": "s3://sentinel-s2-l2a",
                            },
                            "B07": {
                                "title": "Band 7",
                                "type": "image/jp2",
                                "roles": ["data"],
                                "gsd": 20,
                                "eo:bands": [
                                    {
                                        "name": "B07",
                                        "center_wavelength": 0.7825,
                                        "full_width_half_max": 0.028,
                                    }
                                ],
                                "href": "s3://sentinel-s2-l2a",
                            },
                            "B08": {
                                "title": "Band 8 (nir)",
                                "type": "image/jp2",
                                "roles": ["data"],
                                "gsd": 10,
                                "eo:bands": [
                                    {
                                        "name": "B08",
                                        "common_name": "nir",
                                        "center_wavelength": 0.8351,
                                        "full_width_half_max": 0.145,
                                    }
                                ],
                                "href": "s3://sentinel-s2-l2a",
                            },
                            "B8A": {
                                "title": "Band 8A",
                                "type": "image/jp2",
                                "roles": ["data"],
                                "gsd": 20,
                                "eo:bands": [
                                    {
                                        "name": "B8A",
                                        "center_wavelength": 0.8648,
                                        "full_width_half_max": 0.033,
                                    }
                                ],
                                "href": "s3://sentinel-s2-l2a",
                            },
                            "B09": {
                                "title": "Band 9",
                                "type": "image/jp2",
                                "roles": ["data"],
                                "gsd": 60,
                                "eo:bands": [
                                    {
                                        "name": "B09",
                                        "center_wavelength": 0.945,
                                        "full_width_half_max": 0.026,
                                    }
                                ],
                                "href": "s3://sentinel-s2-l2a",
                            },
                            "B11": {
                                "title": "Band 11 (swir16)",
                                "type": "image/jp2",
                                "roles": ["data"],
                                "gsd": 20,
                                "eo:bands": [
                                    {
                                        "name": "B11",
                                        "common_name": "swir16",
                                        "center_wavelength": 1.6137,
                                        "full_width_half_max": 0.143,
                                    }
                                ],
                                "href": "s3://sentinel-s2-l2a",
                            },
                            "B12": {
                                "title": "Band 12 (swir22)",
                                "type": "image/jp2",
                                "roles": ["data"],
                                "gsd": 20,
                                "eo:bands": [
                                    {
                                        "name": "B12",
                                        "common_name": "swir22",
                                        "center_wavelength": 2.22024,
                                        "full_width_half_max": 0.242,
                                    }
                                ],
                                "href": "s3://sentinel-s2-l2a",
                            },
                            "AOT": {
                                "title": "Aerosol Optical Thickness (AOT)",
                                "type": "image/jp2",
                                "roles": ["data"],
                                "href": "s3://sentinel-s2-l2a",
                            },
                            "WVP": {
                                "title": "Water Vapour (WVP)",
                                "type": "image/jp2",
                                "roles": ["data"],
                                "href": "s3://sentinel-s2-l2a",
                            },
                            "SCL": {
                                "title": "Scene Classification Map (SCL)",
                                "type": "image/jp2",
                                "roles": ["data"],
                                "href": "s3://sentinel-s2-l2a",
                            },
                        },
                        "links": [
                            {
                                "rel": "self",
                                "href": "https://test",
                                "type": "application/json",
                            },
                            {
                                "rel": "canonical",
                                "href": "https://test",
                                "type": "application/json",
                            },
                            {
                                "title": "sentinel-s2-l2a-aws",
                                "rel": "via-cirrus",
                                "href": "https://test",
                            },
                        ],
                    }
                ],
                "process": [
                    {
                        "input_collections": ["sentinel-s2-l2a"],
                        "workflow": "mirror",
                        "upload_options": {
                            "path_template": "s3://sentinel-cogs",
                            "public_assets": "ALL",
                            "collections": {"sentinel-s2-l2a-cogs": ".*"},
                            "headers": {
                                "CacheControl": "public, max-age=31536000, immutable"
                            },
                        },
                        "tasks": {
                            "copy-assets": {
                                "batch": False,
                                "assets": [],
                                "drop_assets": ["visual_20m", "visual_60m"],
                            },
                            "convert-to-cog": {
                                "batch": True,
                                "assets": {
                                    "overview": {
                                        "nodata": 0,
                                        "blocksize": 128,
                                        "overview_blocksize": 64,
                                        "overview_resampling": "average",
                                    },
                                    "visual": {
                                        "nodata": 0,
                                        "blocksize": 1024,
                                        "overview_blocksize": 512,
                                        "overview_resampling": "average",
                                    },
                                    "B01": {
                                        "nodata": 0,
                                        "blocksize": 256,
                                        "overview_blocksize": 128,
                                        "overview_resampling": "average",
                                    },
                                    "B02": {
                                        "nodata": 0,
                                        "blocksize": 1024,
                                        "overview_blocksize": 512,
                                        "overview_resampling": "average",
                                    },
                                    "B03": {
                                        "nodata": 0,
                                        "blocksize": 1024,
                                        "overview_blocksize": 512,
                                        "overview_resampling": "average",
                                    },
                                    "B04": {
                                        "nodata": 0,
                                        "blocksize": 1024,
                                        "overview_blocksize": 512,
                                        "overview_resampling": "average",
                                    },
                                    "B05": {
                                        "nodata": 0,
                                        "blocksize": 512,
                                        "overview_blocksize": 256,
                                        "overview_resampling": "average",
                                    },
                                    "B06": {
                                        "nodata": 0,
                                        "blocksize": 512,
                                        "overview_blocksize": 256,
                                        "overview_resampling": "average",
                                    },
                                    "B07": {
                                        "nodata": 0,
                                        "blocksize": 512,
                                        "overview_blocksize": 256,
                                        "overview_resampling": "average",
                                    },
                                    "B08": {
                                        "nodata": 0,
                                        "blocksize": 1024,
                                        "overview_blocksize": 512,
                                        "overview_resampling": "average",
                                    },
                                    "B8A": {
                                        "nodata": 0,
                                        "blocksize": 512,
                                        "overview_blocksize": 256,
                                        "overview_resampling": "average",
                                    },
                                    "B09": {
                                        "nodata": 0,
                                        "blocksize": 256,
                                        "overview_blocksize": 128,
                                        "overview_resampling": "average",
                                    },
                                    "B11": {
                                        "nodata": 0,
                                        "blocksize": 1024,
                                        "overview_blocksize": 512,
                                        "overview_resampling": "average",
                                    },
                                    "B12": {
                                        "nodata": 0,
                                        "blocksize": 512,
                                        "overview_blocksize": 256,
                                        "overview_resampling": "average",
                                    },
                                    "AOT": {
                                        "nodata": 0,
                                        "blocksize": 256,
                                        "overview_blocksize": 128,
                                        "overview_resampling": "mode",
                                    },
                                    "WVP": {
                                        "nodata": 0,
                                        "blocksize": 1024,
                                        "overview_blocksize": 512,
                                        "overview_resampling": "mode",
                                    },
                                    "SCL": {
                                        "nodata": 0,
                                        "blocksize": 512,
                                        "overview_blocksize": 256,
                                        "overview_resampling": "mode",
                                    },
                                },
                            },
                            "publish": {"public": True},
                        },
                    },
                ],
                "id": "mirror",
            },
        },
    },
    "response": "document",
}


def all_payloads(request_endpoint: str):
    return {
        "payloads": [
            a_payload,
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


# Tests for GET/payloads endpoint


@pytest.mark.asyncio
async def test_get_payloads_no_filter(test_client: TestClient):
    url: str = "/cache"
    response = test_client.get(url)
    assert response.json() == all_payloads(url)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_payloads_filter_limit_only(test_client: TestClient):
    url: str = "/cache?limit=1000"
    response = test_client.get(url)
    assert response.json() == all_payloads(url)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_payloads_filter_limit_process(test_client: TestClient):
    url: str = "/cache?limit=1000&processID=some_workflow"
    response = test_client.get(url)
    assert response.json() == all_payloads(url)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_payloads_filter_only_invalid_process_id(test_client: TestClient):
    response = test_client.get("/cache?limit=1000&processID=hello")
    assert response.json()["payloads"] == []
    assert response.status_code == 200


# Tests for GET /cache/{payload-id} endpoint


@pytest.mark.asyncio
async def test_get_payloadid_match(test_client: TestClient):
    response = test_client.get("/cache/ade69fe7-1d7d-572e-9f36-7242cc2aca77")
    assert response.json() == a_payload_details
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_payloadid_no_match(test_client: TestClient):
    response = test_client.get("/cache/d5d64165-82df-5836-b78e-af4daee55d38")
    assert response.status_code == 404
    assert response.json() == {
        "detail": "No payload that matches payload uuid found",
        "status": 404,
    }


@pytest.mark.asyncio
async def test_retrieve_invalid_payload_cache_details1(test_client: TestClient):
    response = test_client.post(
        "/cache/",
        content="{}",
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_retrieve_invalid_payload_cache_details2(test_client: TestClient):
    response = test_client.post(
        "/cache/",
        content=json.dumps({"inputs": {}}),
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_retrieve_unknown_payload_cache_details(test_client: TestClient):
    response = test_client.post(
        "/cache/",
        content=json.dumps(payload_input_unknown),
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_retrieve_missing_payload_cache_details(test_client: TestClient):
    response = test_client.post(
        "/cache/",
        content=json.dumps(payload_input_missing),
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_retrieve_payload_cache_details(test_client: TestClient):
    response = test_client.post(
        "/processes/mirror/execution",
        content=json.dumps(payload_input_valid),
    )
    assert response.status_code == 201
    response = test_client.post(
        "/cache/",
        content=json.dumps(payload_input_valid),
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_set_payload_cache_invalid_after(test_client: TestClient):
    response = test_client.post(
        "/cache/ade69fe7-1d7d-572e-9f36-7242cc2aca77/invalidate",
        content=json.dumps(
            {
                "invalidAfter": "2023-06-29T18:03:38.478Z",
            }
        ),
    )
    assert response.status_code == 200
    response = test_client.get("/cache/ade69fe7-1d7d-572e-9f36-7242cc2aca77/")
    assert response.json()["invalidAfter"] == "2023-06-29T18:03:38.478000Z"


@pytest.mark.asyncio
async def test_set_payload_cache_invalid_after_invalidate_now(test_client: TestClient):
    response = test_client.post(
        "/cache/ade69fe7-1d7d-572e-9f36-7242cc2aca77/invalidate",
        content=json.dumps({"invalidAfter": "now"}),
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_set_payload_cache_invalid_after_bad_value(
    test_client: TestClient,
):
    response = test_client.post(
        "/cache/ade69fe7-1d7d-572e-9f36-7242cc2aca77/invalidate",
        content=json.dumps({"invalidAfter": "random-string"}),
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_set_payload_cache_invalid_after_non_existing_payload(
    test_client: TestClient,
):
    response = test_client.post(
        "/cache/ade69fe7-1d7d-572e-9f36-7242cc2aca78/invalidate",
        content=json.dumps(
            {
                "invalidAfter": "2023-06-29T18:03:38.478Z",
            }
        ),
    )
    assert response.status_code == 404
