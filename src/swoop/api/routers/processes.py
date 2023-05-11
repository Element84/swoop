from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request
from pydantic import BaseModel

from swoop.api.models import Exception as APIException
from swoop.api.models import (
    Execute,
    InlineResponse200,
    Link,
    Process,
    ProcessList,
    ProcessSummary,
    StatusInfo,
)

DEFAULT_PROCESS_LIMIT = 1000

router: APIRouter = APIRouter(
    tags=["Processes"],
)


class Params(BaseModel):
    process_id: str | None
    version: str | None
    title: str | None
    description: str | None
    handler: str | None
    argo_template: str | None = None
    cache_enabled: bool | None = None


def to_process_summary(workflowConfig: list[dict]) -> Process:
    return ProcessSummary(
        id=workflowConfig["name"],
        title=workflowConfig["name"],
        name=workflowConfig["name"],
        processID=workflowConfig["name"],
        version=workflowConfig["version"],
        description=workflowConfig.get("description"),
        handler=workflowConfig.get("handler"),
        argoTemplate=workflowConfig.get("argo_template"),
        cacheEnabled=workflowConfig.get("cache_enabled"),
        cacheKeyHashIncludes=workflowConfig.get("cache_key_hash_includes"),
        cacheKeyHashExcludes=workflowConfig.get("cache_key_hash_excludes"),
    )


def processes_parameter_translation(workflowConfig: dict) -> dict:
    if workflowConfig.get("process_id"):
        workflowConfig["name"] = workflowConfig.pop("process_id")
    if workflowConfig.get("version"):
        workflowConfig["version"] = int(workflowConfig["version"])
    return workflowConfig


@router.get(
    "/",
    response_model=ProcessList,
    responses={"404": {"model": APIException}},
)
async def list_processes(
    request: Request,
    limit: int = Query(ge=1, default=DEFAULT_PROCESS_LIMIT),
    params: Params = Depends(),
) -> ProcessList | APIException:
    """
    retrieve the list of available processes
    """
    queryparams = processes_parameter_translation(params.dict(exclude_none=True))
    workflows = (
        request.app.state.workflows.get("workflows")
        if request.app.state.workflows.get("workflows")
        else []
    )

    if queryparams and len(workflows) > 0:
        workflows = list(
            filter(
                lambda x: queryparams.items() <= x.items(),
                request.app.state.workflows["workflows"],
            )
        )
    if limit and limit < len(workflows):
        workflows = workflows[:limit]

    return ProcessList(
        processes=[to_process_summary(workflow) for workflow in workflows],
        links=[
            Link(
                href="http://www.example.com",
            )
        ],
    )


@router.get(
    "/{process_id}",
    response_model=Process,
    responses={
        "404": {"model": APIException},
        "500": {"model": APIException},
    },
)
async def get_process_description(
    request: Request, process_id
) -> ProcessSummary | APIException:
    """
    retrieve a process description
    """
    workflows = (
        request.app.state.workflows.get("workflows")
        if request.app.state.workflows.get("workflows")
        else []
    )

    if process_id and len(workflows) > 0:
        workflows = list(
            filter(
                lambda x: process_id == x["name"],
                request.app.state.workflows["workflows"],
            )
        )
    if not workflows:
        raise HTTPException(status_code=404, detail="Process not found")

    return to_process_summary(workflows[0])


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
