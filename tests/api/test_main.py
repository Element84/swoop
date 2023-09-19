import pytest

from ..conftest import inject_database_fixture

inject_database_fixture(["base_01"], __name__)


@pytest.mark.asyncio
async def test_read_main(test_client):
    response = test_client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "title": "swoop-api",
        "description": "Example server implementing the OGC API - Processes 1.0 Standard",
        "links": [
            {"href": "http://testserver/", "rel": "root", "type": "application/json"},
            {"href": "http://testserver/", "rel": "self", "type": "application/json"},
            {
                "href": "http://testserver/openapi.json",
                "rel": "service-desc",
                "type": "application/json",
                "title": "API definition for this endpoint as JSON",
            },
            {
                "href": "http://testserver/docs",
                "rel": "service-doc",
                "type": "text/html",
                "title": "API definition for this endpoint as HTML",
            },
            {
                "href": "http://testserver/conformance",
                "rel": "http://www.opengis.net/def/rel/ogc/1.0/conformance",
                "type": "application/json",
                "title": "API conformance classes implemented by this server",
            },
            {
                "href": "http://testserver/processes",
                "rel": "http://www.opengis.net/def/rel/ogc/1.0/processes",
                "type": "application/json",
                "title": "Metadata about the processes supported by this API",
            },
            {
                "href": "http://testserver/jobs",
                "rel": "http://www.opengis.net/def/rel/ogc/1.0/job-list",
                "type": "application/json",
                "title": "List jobs run by this serivce",
            },
            {
                "href": "http://testserver/cache",
                "rel": "http://www.opengis.net/def/rel/ogc/1.0/cache-list",
                "type": "application/json",
                "title": "List cached input payload entries",
            },
        ],
    }


@pytest.mark.asyncio
async def test_conformance(test_client):
    response = test_client.get("/conformance")
    assert response.status_code == 200
    assert response.json() == {
        "conformsTo": [
            "http://www.opengis.net/spec/ogcapi-common-1/1.0/conf/core",
            "http://www.opengis.net/spec/ogcapi-common-1/1.0/conf/json",
            "http://www.opengis.net/spec/ogcapi-common-1/1.0/conf/oas30",
            "http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/core",
            "http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/json",
            "http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/oas30",
            "http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/ogc-process-description",
            "http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/job-list",
            "http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/cache",
        ],
        "links": [
            {"href": "http://testserver/", "rel": "root", "type": "application/json"},
            {
                "href": "http://testserver/conformance",
                "rel": "self",
                "type": "application/json",
            },
        ],
    }
