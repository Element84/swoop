from fastapi.testclient import TestClient
import pytest


@pytest.mark.asyncio
async def test_read_main(test_app):
    with TestClient(test_app) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {
            "description": (
                "Example server implementing the OGC API - Processes 1.0 Standard"
            ),
            "links": [
                {
                    "href": "http://testserver/conformance",
                    "hreflang": None,
                    "rel": "http://www.opengis.net/def/rel/ogc/1.0/conformance",
                    "title": None,
                    "type": "application/json",
                },
            ],
            "title": "Example processing server",
        }
