from __future__ import annotations

import logging
from typing import Annotated
from uuid import UUID

from buildpg import V, funcs, render
from fastapi import APIRouter, HTTPException, Query, Request

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
async def list_jobs(
    request: Request,
    limit: int = Query(ge=1, default=DEFAULT_JOB_LIMIT),
    processID: Annotated[list[str] | None, Query()] = None,
    jobID: Annotated[list[UUID] | None, Query()] = None,
    types: Annotated[list[str] | None, Query(alias="type")] = None,
    status: Annotated[list[StatusCode], Query()] = None,
    swoopStatus: Annotated[list[SwoopStatusCode], Query()] = None,
    datetime: Annotated[str, Query()] = None,
) -> JobList | APIException:
    """
    retrieve the list of jobs.
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

    proc_clause = V("a.action_name") == funcs.any(processID)
    type_clause = V("a.handler_type") == funcs.any(types)
    job_clause = V("a.action_uuid") == funcs.any(jobID)
    status_clause = V("t.status") == funcs.any(statuses)
    swoop_status_clause = V("t.status") == funcs.any(swoop_status)

    async with request.app.state.readpool.acquire() as conn:
        q, p = render(
            """
            SELECT
            *
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
            LIMIT :limit::integer;
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
            start_datetime=start,
            end_datetime=end,
            dt=dt,
            limit=limit,
        )
        records = await conn.fetch(q, *p)

    return JobList(
        jobs=[StatusInfo.from_action_record(group, request) for group in records],
        links=[
            Link.root_link(request),
            Link.self_link(href=str(request.url)),
        ],
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
async def get_job_status(request: Request, jobID: UUID) -> StatusInfo | APIException:
    """
    retrieve the status of a job
    """
    async with request.app.state.readpool.acquire() as conn:
        q, p = render(
            """
                SELECT
                *
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
            raise HTTPException(status_code=404, detail="Job not found")

        return StatusInfo.from_action_record(record, request)


@router.get(
    "/{jobID}/results",
    response_model=Results,
    responses={
        "404": {"model": APIException},
        "500": {"model": APIException},
    },
)
async def get_job_result(
    request: Request,
    jobID,
) -> Results | APIException:
    """
    retrieve the result(s) of a job
    """
    results = request.app.state.io.get_object(f"/execution/{jobID}/output.json")

    if not results:
        raise HTTPException(status_code=404, detail="Job output not found")

    return results


@router.get(
    "/{jobID}/inputs",
    response_model=dict,
    responses={
        "404": {"model": APIException},
        "500": {"model": APIException},
    },
)
async def get_job_inputs(request: Request, jobID) -> dict | APIException:
    """
    retrieve the input payload of a job
    """
    payload = request.app.state.io.get_object(f"/execution/{jobID}/input.json")

    if not payload:
        raise HTTPException(status_code=404, detail="Job input payload not found")

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
