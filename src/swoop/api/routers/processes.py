from __future__ import annotations

import json
from typing import Annotated

from buildpg import Values, render
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import RedirectResponse

from swoop.api.models.jobs import StatusInfo
from swoop.api.models.shared import APIException, Link
from swoop.api.models.workflows import (
    Execute,
    Process,
    ProcessList,
    Workflow,
    Workflows,
)
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
    lastID: Annotated[str | None, Query(alias="lastID")] = None,
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

    index = 0
    if lastID:
        for w in workflows:
            index += 1
            if w.id == lastID:
                break
        workflows = workflows[index:] if index < len(workflows) else []

    links = [
        Link.root_link(request),
        Link.self_link(href=str(request.url)),
    ]

    if limit and limit < len(workflows):
        links.append(
            Link.next_link(
                href=str(
                    request.url.include_query_params(lastID=workflows[limit - 1].id)
                ),
            )
        )
        workflows = workflows[:limit]

    return ProcessList(
        processes=[
            workflow.to_process_summary(request=request) for workflow in workflows
        ],
        links=links,
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

    workflows: Workflows = request.app.state.workflows

    try:
        workflow = workflows[processID]
    except KeyError:
        raise HTTPException(status_code=404, detail="Workflow not found")

    payload_uuid = workflow.generate_payload_uuid(payload)

    # cut the uuid down into a 32-bit int for use as a lock value
    lock_id = payload_uuid.int & 0xFFFF

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
                    :payload_uuid,
                    :wf_version::smallint
                )
                """,
                payload_uuid=payload_uuid,
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
                ON CONFLICT (payload_uuid) DO UPDATE
                SET invalid_after = NULL
                """,
                values=Values(
                    payload_uuid=payload_uuid,
                    workflow_name=workflow.id,
                ),
            )
            await conn.execute(q, *p)

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
                    payload_uuid=payload_uuid,
                ),
            )
            action_uuid = await conn.fetchval(q, *p)

            request.app.state.io.put_object(
                object_name=f"executions/{action_uuid}/input.json",
                object_content=json.dumps(payload.dict()),
            )

    return await get_workflow_execution_details(request, jobID=action_uuid)
