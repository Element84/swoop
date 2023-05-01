from __future__ import annotations
from datetime import datetime


from fastapi import APIRouter, Path, Query, Request

from swoop.api.models import (
    Exception as APIException,
    Execute,
    InlineResponse200,
    Process,
    ProcessList,
    StatusInfo,
)


DEFAULT_PROCESS_LIMIT = 1000

router: APIRouter = APIRouter(
    tags=["Processes"],
)


# TODO - REMOVE ME - Temporary example, for basic testing
@router.get("/test")
async def test(request: Request):
    async with request.app.state.readpool.acquire() as conn:
       rows = await conn.fetch("SELECT * FROM swoop.action")
       return [dict(r) for r in rows]


@router.get(
    "/",
    response_model=ProcessList,
    responses={"404": {"model": APIException}},
)
def list_processes(
    limit: int = Query(ge=1, default=DEFAULT_PROCESS_LIMIT),
    process_id: list[str] | None = Query(default=None),
    collection_id: list[str] | None = Query(default=None),
    item_id: list[str] | None = Query(default=None),
    start_datetime: datetime | None = None,
    end_datetime: datetime | None = None,
    parent_id: list[str] | None = Query(default=None),
) -> ProcessList | APIException:
    """
    retrieve the list of available processes
    """
    pass


@router.get(
    "/{process_id}",
    response_model=Process,
    responses={
        "404": {"model": APIException},
        "500": {"model": APIException},
    },
)
def get_process_description(
    process_id: str = Path(..., alias="processID")
) -> Process | APIException:
    """
    retrieve a process description
    """
    pass


@router.get("/{process_id}/definition")
async def get_process_definition(process_id: str = Path(..., alias="processID")) -> str:
    """
    retrieve a process definition
    """
    pass


@router.post(
    "/{process_id}/execution",
    response_model=InlineResponse200,
    responses={
        "201": {"model": StatusInfo},
        "404": {"model": APIException},
        "500": {"model": APIException},
    },
)
def execute_process(
    process_id: str = Path(..., alias="processID"), body: Execute = ...
) -> InlineResponse200 | StatusInfo | APIException:
    """
    execute a process.
    """
    pass
