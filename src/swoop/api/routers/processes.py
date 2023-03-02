from __future__ import annotations

from typing import Union

from fastapi import APIRouter, Path, Query

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


@router.get('/', response_model=ProcessList)
def list_processes(
    limit: int = Query(ge=1, default=DEFAULT_PROCESS_LIMIT),
) -> ProcessList:
    """
    retrieve the list of available processes
    """
    pass


@router.get(
    '/{process_id}',
    response_model=Process,
    responses={'404': {'model': APIException}},
)
def get_process_description(
    process_id: str = Path(..., alias='processID')
) -> Union[Process, APIException]:
    """
    retrieve a process description
    """
    pass


@router.get("/{process_id}/definition")
async def get_process_definition(
    process_id: str = Path(..., alias='processID')
) -> str:
    """
    retrieve a process definition
    """
    pass


@router.post(
    '/{process_id}/execution',
    response_model=InlineResponse200,
    responses={
        '201': {'model': StatusInfo},
        '404': {'model': APIException},
        '500': {'model': APIException},
    },
)
def execute_process(
    process_id: str = Path(..., alias='processID'),
    body: Execute = ...
) -> Union[InlineResponse200, StatusInfo, APIException]:
    """
    execute a process.
    """
    pass
