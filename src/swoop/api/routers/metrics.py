from __future__ import annotations
from datetime import datetime


from fastapi import APIRouter, Query

from ..models import (
    Exception as APIException,
    Counts,
    Events,
)


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
    process_id: list[str] | None = Query(default=None),
    collection_id: list[str] | None = Query(default=None),
    item_id: list[str] | None = Query(default=None),
    start_datetime: datetime | None = None,
    end_datetime: datetime | None = None,
    parent_id: list[str] | None = Query(default=None),
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
    process_id: list[str] | None = Query(default=None),
    collection_id: list[str] | None = Query(default=None),
    item_id: list[str] | None = Query(default=None),
    start_datetime: datetime | None = None,
    end_datetime: datetime | None = None,
    parent_id: list[str] | None = Query(default=None),
) -> Events | APIException:
    """
    Retrieve execution count summary.
    """
    pass
