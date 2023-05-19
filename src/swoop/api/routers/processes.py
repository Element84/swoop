from __future__ import annotations

import json
import uuid

from buildpg import render
from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request
from pydantic import BaseModel

from swoop.api.models import Exception as APIException
from swoop.api.models import Link, Process, ProcessList, ProcessSummary, StatusInfo
from swoop.api.models.workflows import Execute, Workflow
from swoop.api.routers.jobs import get_job_status

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


def to_process_summary(workflowConfig: Workflow) -> Process:
    return ProcessSummary(
        id=workflowConfig.name,
        title=workflowConfig.name,
        name=workflowConfig.name,
        processID=workflowConfig.name,
        version=workflowConfig.version,
        description=workflowConfig.description,
        handler=workflowConfig.handler,
        # argoTemplate=workflowConfig.workflow_template,
        cacheKeyHashIncludes=workflowConfig.cacheKeyHashIncludes,
        cacheKeyHashExcludes=workflowConfig.cacheKeyHashExcludes,
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
        else {}
    )

    workflows = list(workflows.values())

    if queryparams and len(workflows) > 0:
        workflows = list(
            filter(
                lambda x: queryparams.items() <= vars(x).items(),
                workflows,
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
        else {}
    )

    if process_id and len(workflows.keys()) > 0:
        if process_id in workflows:
            workflow = workflows[process_id]
        else:
            raise HTTPException(status_code=404, detail="Process not found")

    return to_process_summary(workflow)


@router.get("/{process_id}/definition")
async def get_process_definition(process_id: str = Path(..., alias="processID")) -> str:
    """
    retrieve a process definition
    """
    pass


@router.post(
    "/{process_id}/execution",
    response_model=StatusInfo,
    responses={
        "201": {"model": StatusInfo},
        "404": {"model": APIException},
        "422": {"model": APIException},
    },
)
async def execute_process(
    process_id: str, request: Request, body: Execute
) -> StatusInfo | APIException:
    """
    execute a process.
    """

    workflows = (
        request.app.state.workflows.get("workflows")
        if request.app.state.workflows.get("workflows")
        else {}
    )

    if process_id and len(workflows.keys()) > 0:
        if process_id in workflows:
            workflow = workflows[process_id]
        else:
            raise HTTPException(status_code=404, detail="Process not found")

    # Generate a UUID
    action_uuid = uuid.uuid4()

    # Write to object storage

    request.app.state.io.put_object(
        object_name=f"executions/{action_uuid}/input.json",
        object_content=json.dumps(body.dict()["inputs"]),
    )

    async with request.app.state.readpool.acquire() as conn:
        # Insert a dummy row into payload_cache table
        # To be removed later
        pl_uuid = "debeb36c-e09e-41c3-bdc5-596287fe724a"

        q, p = render(
            f"""
                INSERT INTO swoop.payload_cache(payload_uuid,
                    workflow_version, workflow_name)
                VALUES ('{pl_uuid}',2,'mirror');
            """,
        )
        await conn.fetchrow(q, *p)

        q, p = render(
            f"""
                INSERT INTO swoop.action(action_uuid, action_type,
                    action_name, handler_name, parent_uuid, payload_uuid)
                VALUES ('{action_uuid}','workflow','{workflow.name}',
                '{workflow.handler}','{uuid.uuid4()}','{pl_uuid}');
            """,
        )
        await conn.fetchrow(q, *p)

    return await get_job_status(request, job_id=action_uuid)
