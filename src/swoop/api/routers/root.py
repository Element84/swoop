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
    return LandingPage(
        title="Example processing server",
        description="Example server implementing the OGC API - Processes 1.0 Standard",
        links=[
            Link(
                href=str(request.url_for("get_conformance_classes")),
                rel="http://www.opengis.net/def/rel/ogc/1.0/conformance",
                type="application/json",
                hreflang=None,
            ),
        ],
    )


@router.get(
    "/conformance",
    response_model=ConfClasses,
    responses={"500": {"model": APIException}},
    tags=["ConformanceDeclaration"],
)
def get_conformance_classes() -> ConfClasses | APIException:
    """
    information about standards that this API conforms to
    """
    pass
