from __future__ import annotations

import json

from buildpg import Values, render
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from fastapi.responses import RedirectResponse
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


def to_process_summary(workflowConfig: Workflow) -> ProcessSummary:
    return ProcessSummary(
        id=workflowConfig.name,
        title=workflowConfig.name,
        name=workflowConfig.name,
        processID=workflowConfig.name,
        version=str(workflowConfig.version),
        description=workflowConfig.description,
        handler=workflowConfig.handler,
        cacheKeyHashIncludes=workflowConfig.cache_key_hash_includes,
        cacheKeyHashExcludes=workflowConfig.cache_key_hash_excludes,
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
    workflows: list[Workflow] = list(request.app.state.workflows.values())

    if queryparams:
        workflows = [wf for wf in workflows if queryparams.items() <= wf.dict().items()]

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
    workflows = request.app.state.workflows

    try:
        workflow = workflows[process_id]
    except KeyError:
        raise HTTPException(status_code=404, detail="Process not found")

    return to_process_summary(workflow)


@router.post(
    "/{process_id}/execution",
    response_model=None,
    responses={
        "201": {"model": StatusInfo},
        "303": {"description": "See existing job"},
        "404": {"model": APIException},
        "422": {"model": APIException},
    },
    status_code=201,
)
async def execute_process(
    process_id: str,
    request: Request,
    body: Execute,
    response: Response,
) -> RedirectResponse | StatusInfo | APIException:
    """
    execute a process.
    """

    payload = body.dict().get("inputs", {}).get("payload", {})

    wf_name = payload.get("process", [{}])[0].get("workflow")
    if process_id != wf_name:
        raise HTTPException(
            status_code=422, detail="Workflow name in payload does not match process ID"
        )

    workflows = request.app.state.workflows

    try:
        workflow = workflows[process_id]
    except KeyError:
        raise HTTPException(status_code=404, detail="Process not found")

    hashed_pl = workflow.hash_payload(payload=payload)

    lock_id = int.from_bytes(hashed_pl[:3])

    async with request.app.state.writepool.acquire() as conn:
        async with conn.transaction():
            q, p = render(
                """
                SELECT pg_advisory_xact_lock(
                    to_regclass('swoop.payload_cache')::oid::integer,:lock_id
                )
                """,
                lock_id=lock_id,
            )

            await conn.execute(q, *p)

            q, p = render(
                """
                SELECT swoop.find_cached_action_for_payload(
                    :plhash,
                    :wf_version::smallint
                )
                """,
                plhash=hashed_pl,
                wf_version=workflow.version,
            )
            action_uuid = await conn.fetchval(q, *p)

            if action_uuid:
                return RedirectResponse(
                    request.url_for("get_job_status", job_id=action_uuid),
                    status_code=303,
                )

            q, p = render(
                """
                INSERT INTO swoop.payload_cache (:values__names) VALUES :values
                ON CONFLICT (payload_hash) DO UPDATE
                SET invalid_after = NULL
                RETURNING payload_uuid;
                """,
                values=Values(payload_hash=hashed_pl, workflow_name=workflow.name),
            )
            pl_uuid = await conn.fetchval(q, *p)

            # Insert into action table

            q, p = render(
                """
                INSERT INTO swoop.action (:values__names)
                VALUES :values
                RETURNING action_uuid
                """,
                values=Values(
                    action_type="workflow",
                    action_name=workflow.name,
                    handler_name=workflow.handler,
                    workflow_version=workflow.version,
                    payload_uuid=pl_uuid,
                ),
            )
            rec = await conn.fetchrow(q, *p)
            action_uuid = str(rec["action_uuid"])

            # Write to object storage

            request.app.state.io.put_object(
                object_name=f"executions/{action_uuid}/input.json",
                object_content=json.dumps(payload),
            )

    return await get_job_status(request, job_id=action_uuid)
