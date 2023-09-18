from __future__ import annotations

from fastapi import APIRouter, Request

from swoop.api.models.root import ConfClasses, LandingPage
from swoop.api.models.shared import APIException, Link

router: APIRouter = APIRouter()


@router.get(
    "/",
    response_model=LandingPage,
    responses={"500": {"model": APIException}},
    tags=["Capabilities"],
)
def get_landing_page(request: Request) -> LandingPage | APIException:
    """
    landing page of this API
    """
    links = [
        Link.root_link(request),
        Link.self_link(href=str(request.url)),
        Link(
            href=str(request.url_for("openapi")),
            rel="service-desc",
            type="application/json",
            title="API definition for this endpoint as JSON",
        ),
        Link(
            href=str(request.url_for("swagger_ui_html")),
            rel="service-doc",
            type="text/html",
            title="API definition for this endpoint as HTML",
        ),
        Link(
            href=str(request.url_for("get_conformance_classes")),
            rel="http://www.opengis.net/def/rel/ogc/1.0/conformance",
            type="application/json",
            title="API conformance classes implemented by this server",
        ),
        Link(
            href=str(request.url_for("list_workflows")),
            rel="http://www.opengis.net/def/rel/ogc/1.0/processes",
            type="application/json",
            title="Metadata about the processes supported by this API",
        ),
        Link(
            href=str(request.url_for("list_workflow_executions")),
            rel="http://www.opengis.net/def/rel/ogc/1.0/job-list",
            type="application/json",
            title="List jobs run by this serivce",
        ),
        Link(
            href=str(request.url_for("list_input_payload_cache_entries")),
            rel="http://www.opengis.net/def/rel/ogc/1.0/cache-list",
            type="application/json",
            title="List cached input payload entries",
        ),
    ]

    # TODO: how to make title/description configurable
    return LandingPage(
        title="swoop-api",
        description="Example server implementing the OGC API - Processes 1.0 Standard",
        links=links,
    )


@router.get(
    "/conformance",
    response_model=ConfClasses,
    responses={"500": {"model": APIException}},
    tags=["ConformanceDeclaration"],
)
def get_conformance_classes(request: Request) -> ConfClasses | APIException:
    """
    information about standards that this API conforms to
    """
    return ConfClasses(
        conformsTo=[
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
        links=[
            Link.root_link(request),
            Link.self_link(href=str(request.url)),
        ],
    )
