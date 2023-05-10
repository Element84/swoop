from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel
from asyncpg import Record
from buildpg import render
from fastapi import APIRouter, Path, Query, Request, Depends, HTTPException

from ..models import (
    Exception as APIException,
    JobList,
    Link,
    Results,
    StatusInfo,
    InlineResponse200,
)
import logging

logger = logging.getLogger("uvicorn")
logger.setLevel(logging.INFO)
DEFAULT_JOB_LIMIT = 1000
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

router: APIRouter = APIRouter(
    tags=["Jobs"],
)


### Query Param Mapping Guide
#
# Job requests contain params that may not directly map to a DB field.
# Below is an explanation of what each query param maps to.
#
# A join between the 'action' and 'thread' tables is necessary before filtering
# by certain params, and generating a StatusInfo response object.
#
#   process_id -> action.action_name
#   start_datetime -> event.event_time = {start_datetime}, and event.status = 'RUNNING'
#   end_datetime -> event.event_time = {end_datetime}, and event.status = 'COMPLETED'
#   parent_id -> action.parent_uuid
#   job_id -> action.action_uuid


status_dict = {
    "PENDING": "accepted",
    "QUEUED": "running",  # ?
    "RUNNING": "running",
    "SUCCESSFUL": "successful",
    "FAILED": "failed",
    "CANCELED": "dismissed",
    "TIMED_OUT": "failed",  # ?
    "UNKNOWN": "failed",  # ?
    "BACKOFF": "failed",  # ?
    "INVALID": "failed",  # ?
    "RETRIES_EXHAUSTED": "failed",  # ?
    #'INFO': '?' # ?
}


def to_status_info(records: list[Record]) -> StatusInfo:
    return StatusInfo(
        processID=records["action_name"],
        type="process",
        jobID=str(records["action_uuid"]),
        status=status_dict[records["status"]],
        updated=records["last_update"],
        parentID=records["parent_uuid"],
    )


class Params(BaseModel):
    process_id: str | None
    # collection_id: str | None  # TODO - possibly named just 'collection'
    # item_id: str | None        # TODO
    start_datetime: datetime | None
    end_datetime: datetime | None
    parent_id: str | None


@router.get(
    "/",
    response_model=JobList,
    responses={"404": {"model": APIException}},
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
AND (:parent_id::bigint IS NULL OR a.parent_uuid = :parent_id::bigint)
AND (:job_id::uuid IS NULL OR a.action_uuid = :job_id::uuid)
AND (
(a.created_at >= DATE(:start_datetime::TIMESTAMPTZ)
OR :start_datetime::TIMESTAMPTZ IS NULL)
AND
(a.created_at <= :end_datetime::TIMESTAMPTZ OR :end_datetime::TIMESTAMPTZ IS NULL)
)
LIMIT :limit::integer;
            """,
            process_id=queryparams.get(
                "process_id"
            ),  # we should account for non-existent keys
            parent_id=int(queryparams.get("parent_id"))
            if queryparams.get("parent_id")
            else None,
            job_id=queryparams.get("job_id"),
            start_datetime=queryparams.get("start_datetime"),
            end_datetime=queryparams.get("end_datetime"),
            limit=limit,
        )
        records = await conn.fetch(q, *p)

    return JobList(
        jobs=[to_status_info(group) for group in records],
        links=[
            Link(
                href="http://www.example.com",
            )
        ],
    )


@router.get(
    "/{job_id}",
    response_model=StatusInfo,
    responses={
        "404": {"model": APIException},
        "500": {"model": APIException},
    },
)
async def get_job_status(request: Request, job_id) -> StatusInfo | APIException:
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
            job_id=job_id,
        )
        record = await conn.fetchrow(q, *p)
        if not record:
            raise HTTPException(status_code=404, detail="Job not found")

        return to_status_info(record)


@router.delete(
    "/{job_id}",
    response_model=StatusInfo,
    responses={
        "404": {"model": APIException},
        "500": {"model": APIException},
    },
)
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
            job_id=job_id,
        )
        record = await conn.fetchrow(q, *p)
        if not record:
            raise HTTPException(status_code=404, detail="Job not found")

        # TODO - Fix this with correct Results data
        return {"example": "example results"}


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
    async with request.app.state.readpool.acquire() as conn:
        q, p = render(
            """
                SELECT
                1
                FROM swoop.action a
                WHERE a.action_type = 'workflow'
                AND a.action_uuid = :job_id::uuid;
            """,
            job_id=job_id,
        )
        job = await conn.fetchval(q, *p)

        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        # TODO - implement this later
        return {"example": "example payload"}


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
