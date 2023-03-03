from __future__ import annotations


from fastapi import APIRouter

from ..models import (
    ConfClasses,
    Exception as APIException,
    LandingPage,
)


router: APIRouter = APIRouter()


@router.get(
    "/",
    response_model=LandingPage,
    responses={"500": {"model": APIException}},
    tags=["Capabilities"],
)
def get_landing_page() -> LandingPage | APIException:
    """
    landing page of this API
    """
    pass


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
