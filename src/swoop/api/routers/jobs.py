from __future__ import annotations

import logging
from datetime import datetime

from buildpg import render
from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request
from pydantic import BaseModel

from swoop.api.models.jobs import JobList, StatusInfo
from swoop.api.models.shared import APIException, InlineResponse200, Link, Results

logger = logging.getLogger("uvicorn")
logger.setLevel(logging.INFO)
DEFAULT_JOB_LIMIT = 1000
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

router: APIRouter = APIRouter(
    tags=["Jobs"],
)


class Params(BaseModel):
    processID: str | None
    startDatetime: datetime | None
    endDatetime: datetime | None
    parentID: str | None


@router.get(
    "/",
    response_model=JobList,
    responses={"404": {"model": APIException}},
    response_model_exclude_unset=True,
)
async def list_jobs(
    request: Request,
    limit: int = Query(ge=1, default=DEFAULT_JOB_LIMIT),
    params: Params = Depends(),
) -> JobList | APIException:
    """
    retrieve the list of jobs.
    """
    queryparams = params.dict(exclude_none=True)
    async with request.app.state.readpool.acquire() as conn:
        q, p = render(
            """
            SELECT
            *
            FROM swoop.action a
            INNER JOIN swoop.thread t
            ON t.action_uuid = a.action_uuid
            WHERE a.action_type = 'workflow'
            AND (:process_id::text IS NULL OR a.action_name = :process_id::text)
            AND (:parent_id::uuid IS NULL OR a.parent_uuid = :parent_id::uuid)
            AND (:job_id::uuid IS NULL OR a.action_uuid = :job_id::uuid)
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
            LIMIT :limit::integer;
            """,
            process_id=queryparams.get(
                "processID"
            ),  # we should account for non-existent keys
            parent_id=queryparams.get("parentID"),
            job_id=queryparams.get("jobID"),
            start_datetime=queryparams.get("startDatetime"),
            end_datetime=queryparams.get("endDatetime"),
            limit=limit,
        )
        records = await conn.fetch(q, *p)

    return JobList(
        jobs=[StatusInfo.from_action_record(group) for group in records],
        links=[
            Link(
                href="http://www.example.com",
            )
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
async def get_job_status(request: Request, jobID) -> StatusInfo | APIException:
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

        return StatusInfo.from_action_record(record)


def cancel_job(
    job_id: str = Path(..., alias="jobId"),
) -> StatusInfo | APIException:
    """
    cancel a job execution, remove a finished job
    """
    pass


@router.get(
    "/{job_id}/results",
    response_model=Results,
    responses={
        "404": {"model": APIException},
        "500": {"model": APIException},
    },
)
async def get_job_result(
    request: Request,
    job_id,
) -> Results | APIException:
    """
    retrieve the result(s) of a job
    """
    results = request.app.state.io.get_object("/execution/%s/output.json" % job_id)

    if not results:
        raise HTTPException(status_code=404, detail="Job output not found")

    return results


@router.get(
    "/{job_id}/payload",
    response_model=dict,
    responses={
        "404": {"model": APIException},
        "500": {"model": APIException},
    },
)
async def get_job_payload(request: Request, job_id) -> dict | APIException:
    """
    retrieve the input payload of a job
    """
    payload = request.app.state.io.get_object("/execution/%s/input.json" % job_id)

    if not payload:
        raise HTTPException(status_code=404, detail="Job input payload not found")

    return payload


@router.post(
    "/{job_id}/rerun",
    response_model=InlineResponse200,
    responses={
        "201": {"model": StatusInfo},
        "404": {"model": APIException},
        "500": {"model": APIException},
    },
)
def rerun_job(
    job_id: str = Path(..., alias="jobId"),
) -> InlineResponse200 | StatusInfo | APIException:
    """
    rerun a job.
    """
    pass
