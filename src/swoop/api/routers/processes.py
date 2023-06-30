from __future__ import annotations

import json
from typing import Annotated

from buildpg import Values, render
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import RedirectResponse

from swoop.api.models.jobs import StatusInfo
from swoop.api.models.shared import APIException, Link
from swoop.api.models.workflows import Execute, Process, ProcessList, Workflow
from swoop.api.routers.jobs import get_workflow_execution_details

DEFAULT_PROCESS_LIMIT = 1000

router: APIRouter = APIRouter(
    tags=["Processes"],
)


@router.get(
    "/",
    response_model=ProcessList,
    responses={},
    response_model_exclude_unset=True,
)
async def list_workflows(
    request: Request,
    limit: int = Query(ge=1, default=DEFAULT_PROCESS_LIMIT),
    handlers: Annotated[list[str] | None, Query(alias="handler")] = None,
    types: Annotated[list[str] | None, Query(alias="type")] = None,
) -> ProcessList | APIException:
    """
    Returns a list of all available workflows
    """
    workflows: list[Workflow] = list(request.app.state.workflows.values())

    if handlers:
        _workflows: list[Workflow] = []
        for handler in handlers:
            _workflows += [wf for wf in workflows if wf.handler_name == handler]
        workflows = _workflows

    if types:
        _workflows: list[Workflow] = []
        for _type in types:
            _workflows += [wf for wf in workflows if wf.handler_type == _type]
        workflows = _workflows

    if limit and limit < len(workflows):
        workflows = workflows[:limit]

    return ProcessList(
        processes=[
            workflow.to_process_summary(request=request) for workflow in workflows
        ],
        links=[
            Link.root_link(request),
            Link.self_link(href=str(request.url)),
        ],
    )


@router.get(
    "/{processID}",
    response_model=Process,
    responses={
        "404": {"model": APIException},
        "500": {"model": APIException},
    },
    response_model_exclude_unset=True,
)
async def get_workflow_description(
    request: Request, processID
) -> Process | APIException:
    """
    Returns workflow details by processID
    """
    workflows = request.app.state.workflows

    try:
        workflow = workflows[processID]
    except KeyError:
        raise HTTPException(status_code=404, detail="Workflow not found")

    return workflow.to_process(request=request)


@router.post(
    "/{processID}/execution",
    response_model=None,
    responses={
        "201": {"model": StatusInfo},
        "303": {"description": "See existing job"},
        "404": {"model": APIException},
        "422": {"model": APIException},
    },
    status_code=201,
    response_model_exclude_unset=True,
)
async def execute_workflow(
    processID: str,
    request: Request,
    body: Execute,
) -> RedirectResponse | StatusInfo | APIException:
    """
    Starts a workflow execution (Job)
    """

    payload = body.inputs.payload

    wf_name = payload.current_process_definition().workflow

    if processID != wf_name:
        raise HTTPException(
            status_code=422, detail="Workflow name in payload does not match process ID"
        )

    workflows = request.app.state.workflows

    try:
        workflow = workflows[processID]
    except KeyError:
        raise HTTPException(status_code=404, detail="Workflow not found")

    hashed_pl = workflow.hash_payload(payload=payload.dict())

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
                    request.url_for(
                        "get_workflow_execution_details", jobID=action_uuid
                    ),
                    status_code=303,
                )

            q, p = render(
                """
                INSERT INTO swoop.payload_cache (:values__names) VALUES :values
                ON CONFLICT (payload_hash) DO UPDATE
                SET invalid_after = NULL
                RETURNING payload_uuid;
                """,
                values=Values(payload_hash=hashed_pl, workflow_name=workflow.id),
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
                    action_name=workflow.id,
                    handler_name=workflow.handler_name,
                    handler_type=workflow.handler_type,
                    workflow_version=workflow.version,
                    payload_uuid=pl_uuid,
                ),
            )
            rec = await conn.fetchrow(q, *p)
            action_uuid = str(rec["action_uuid"])

            # Write to object storage

            request.app.state.io.put_object(
                object_name=f"executions/{action_uuid}/input.json",
                object_content=json.dumps(payload.dict()),
            )

    return await get_workflow_execution_details(request, jobID=action_uuid)
