from __future__ import annotations

import logging
from typing import Annotated
from uuid import UUID

from buildpg import V, funcs, render
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import JSONResponse

from swoop.api.models.jobs import (
    JobList,
    StatusCode,
    StatusInfo,
    SwoopStatusCode,
    status_dict,
)
from swoop.api.models.shared import APIException, Link, Results
from swoop.api.rfc3339 import rfc3339_str_to_datetime, str_to_interval

logger = logging.getLogger(__name__)

DEFAULT_JOB_LIMIT = 1000
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

router: APIRouter = APIRouter(
    tags=["Jobs"],
)


@router.get(
    "/",
    response_model=JobList,
    responses={"404": {"model": APIException}, "422": {"model": APIException}},
    response_model_exclude_unset=True,
)
async def list_workflow_executions(
    request: Request,
    limit: int = Query(ge=1, default=DEFAULT_JOB_LIMIT),
    processID: Annotated[list[str] | None, Query()] = None,
    jobID: Annotated[list[UUID] | None, Query()] = None,
    types: Annotated[list[str] | None, Query(alias="type")] = None,
    status: Annotated[list[StatusCode], Query()] = None,
    swoopStatus: Annotated[list[SwoopStatusCode], Query()] = None,
    datetime: Annotated[str, Query()] = None,
    minDuration: Annotated[int, Query()] = None,
    maxDuration: Annotated[int, Query()] = None,
    lastID: UUID | None = None,
) -> JobList | APIException:
    """
    Returns a list of all available workflow executions
    """

    try:
        if datetime is None:
            start = None
            end = None
            dt = None
        elif "/" in datetime:
            start, end = str_to_interval(datetime)
            dt = None
        else:
            dt = rfc3339_str_to_datetime(datetime)
            start = None
            end = None
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid datetime parameter(s).")

    if status is not None:
        statuses = [
            i for i in status_dict if status_dict[i] in [s.value for s in status]
        ]
    else:
        statuses = None

    if swoopStatus is not None:
        swoop_status = [s.value for s in swoopStatus]
    else:
        swoop_status = None

    duration_status = [
        i
        for i in status_dict
        if status_dict[i] in ["running", "successful", "failed", "dismissed"]
    ]

    completed_status = [
        i
        for i in status_dict
        if status_dict[i] in ["successful", "failed", "dismissed"]
    ]

    proc_clause = V("a.action_name") == funcs.any(processID)
    type_clause = V("a.handler_type") == funcs.any(types)
    job_clause = V("a.action_uuid") == funcs.any(jobID)
    status_clause = V("t.status") == funcs.any(statuses)
    swoop_status_clause = V("t.status") == funcs.any(swoop_status)
    duration_status_clause = V("status") == funcs.any(duration_status)
    completed_status_clause = V("t.status") == funcs.any(completed_status)

    async with request.app.state.readpool.acquire() as conn:
        q, p = render(
            """
            WITH jobs AS (
                SELECT
                    a.action_name,
                    a.action_uuid,
                    a.handler_type,
                    t.status AS status,
                    t.created_at,
                    t.last_update,
                    a.payload_uuid,
                    t.started_at,
                    CASE
                        WHEN t.status = 'RUNNING'
                            THEN EXTRACT(EPOCH FROM (NOW() - t.started_at))
                        WHEN :completed_where
                            THEN EXTRACT(EPOCH FROM (t.last_update - t.started_at))
                    END AS duration
                FROM swoop.action a
                INNER JOIN swoop.thread t
                ON t.action_uuid = a.action_uuid
                WHERE a.action_type = 'workflow'
                AND (:processes::text[] IS NULL OR :proc_where)
                AND (:types::text[] IS NULL OR :type_where)
                AND (:jobs::uuid[] IS NULL OR :job_where)
                AND (:status::text[] IS NULL OR :status_where)
                AND (:swoop_status::text[] IS NULL OR :swoop_status_where)
                AND (
                        (
                            a.created_at >= :start_datetime::TIMESTAMPTZ
                            OR :start_datetime::TIMESTAMPTZ IS NULL
                        )
                        AND
                        (
                            a.created_at <= :end_datetime::TIMESTAMPTZ
                            OR :end_datetime::TIMESTAMPTZ IS NULL
                        )
                )
                AND (
                    a.created_at = :dt::TIMESTAMPTZ
                    OR :dt::TIMESTAMPTZ IS NULL
                )
            )
            SELECT *
            FROM jobs
            WHERE
                (
                    (
                        duration IS NOT NULL

                        AND
                        (
                            duration >= :min_duration::integer
                            OR :min_duration::integer IS NULL
                        )
                        AND
                        (
                            duration <= :max_duration::integer
                            OR :max_duration::integer IS NULL
                        )
                        AND
                        (
                            CASE
                                WHEN :status::text[] IS NULL AND
                                    (:min_duration::integer IS NOT NULL OR
                                    :max_duration::integer IS NOT NULL)
                                THEN :dur_status_where ELSE TRUE
                            END
                        )
                    )

                    OR (
                        CASE
                            WHEN duration IS NULL AND
                                (:min_duration::integer IS NOT NULL OR
                                :max_duration::integer IS NOT NULL)
                            THEN :dur_status_where
                        END
                    )

                    OR (
                        duration IS NULL
                        AND (:min_duration::integer IS NULL AND
                            :max_duration::integer IS NULL)
                    )
                )
                AND
                (:last::uuid IS NULL OR action_uuid < :last)
            ORDER BY action_uuid DESC
            LIMIT :limit
            """,
            processes=processID,
            proc_where=proc_clause,
            types=types,
            type_where=type_clause,
            jobs=jobID,
            job_where=job_clause,
            status=statuses,
            status_where=status_clause,
            swoop_status=swoop_status,
            swoop_status_where=swoop_status_clause,
            dur_status_where=duration_status_clause,
            completed_where=completed_status_clause,
            start_datetime=start,
            end_datetime=end,
            dt=dt,
            limit=limit + 1,
            min_duration=minDuration,
            max_duration=maxDuration,
            last=lastID,
        )
        records = await conn.fetch(q, *p)

    links = [
        Link.root_link(request),
        Link.self_link(href=str(request.url)),
    ]

    if len(records) > limit:
        records.pop(-1)
        lastID = records[-1]["action_uuid"]
        links.append(
            Link.next_link(
                href=str(request.url.include_query_params(lastID=lastID)),
            ),
        )

    return JobList(
        jobs=[StatusInfo.from_action_record(group, request) for group in records],
        links=links,
    )


@router.get(
    "/{jobID}",
    response_model=StatusInfo,
    responses={
        "404": {"model": APIException},
        "500": {"model": APIException},
    },
    response_model_exclude_unset=True,
)
async def get_workflow_execution_details(
    request: Request, jobID: UUID
) -> StatusInfo | APIException:
    """
    Returns workflow execution status by jobID
    """
    async with request.app.state.readpool.acquire() as conn:
        q, p = render(
            """
                SELECT
                    a.action_name,
                    a.action_uuid,
                    t.status,
                    t.created_at,
                    t.last_update,
                    a.payload_uuid,
                    t.started_at
                FROM swoop.action a
                INNER JOIN swoop.thread t
                ON t.action_uuid = a.action_uuid
                WHERE a.action_type = 'workflow'
                AND a.action_uuid = :job_id::uuid;
            """,
            job_id=jobID,
        )
        record = await conn.fetchrow(q, *p)
        if not record:
            raise HTTPException(status_code=404, detail="Workflow execution not found")

        return StatusInfo.from_action_record(record, request)


@router.get(
    "/{jobID}/results",
    response_model=Results,
    responses={
        "404": {"model": APIException},
        "500": {"model": APIException},
    },
)
async def get_workflow_execution_result(
    request: Request,
    jobID,
) -> JSONResponse | APIException:
    """
    Retrieves workflow execution output payload by jobID
    """
    results = request.app.state.io.get_object(f"/executions/{jobID}/output.json")

    if not results:
        raise HTTPException(
            status_code=404, detail="Workflow execution output payload not found"
        )

    return JSONResponse(results)


@router.get(
    "/{jobID}/inputs",
    response_model=dict,
    responses={
        "404": {"model": APIException},
        "500": {"model": APIException},
    },
)
async def get_workflow_execution_inputs(request: Request, jobID) -> dict | APIException:
    """
    Retrieves workflow execution input payload by jobID
    """
    payload = request.app.state.io.get_object(f"/executions/{jobID}/input.json")

    if not payload:
        raise HTTPException(
            status_code=404, detail="Workflow execution input payload not found"
        )

    return payload


# @router.post(
#    "/{jobID}/rerun",
#    response_model=InlineResponse200,
#    responses={
#        "201": {"model": StatusInfo},
#        "404": {"model": APIException},
#        "500": {"model": APIException},
#    },
# )
# def rerun_job(
#    job_id: str = Path(..., alias="jobID"),
# ) -> InlineResponse200 | StatusInfo | APIException:
#    """
#    rerun a job.
#    """
#    pass
