from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Query

from ..models import Counts, Events
from ..models import Exception as APIException

DEFAULT_JOB_LIMIT = 1000

router: APIRouter = APIRouter(
    tags=["Metrics"],
)


@router.get(
    "/counts",
    response_model=Counts,
    responses={"404": {"model": APIException}},
)
def get_execution_counts(
    processID: list[str] | None = Query(default=None),
    collectionID: list[str] | None = Query(default=None),
    itemID: list[str] | None = Query(default=None),
    startDatetime: datetime | None = None,
    endDatetime: datetime | None = None,
    parentID: list[str] | None = Query(default=None),
) -> Counts | APIException:
    """
    Retrieve execution count summary.
    """
    pass


@router.get(
    "/events",
    response_model=Events,
    responses={"404": {"model": APIException}},
)
def get_execution_events(
    processID: list[str] | None = Query(default=None),
    collectionID: list[str] | None = Query(default=None),
    itemID: list[str] | None = Query(default=None),
    startDatetime: datetime | None = None,
    endDatetime: datetime | None = None,
    parentID: list[str] | None = Query(default=None),
) -> Events | APIException:
    """
    Retrieve execution count summary.
    """
    pass
