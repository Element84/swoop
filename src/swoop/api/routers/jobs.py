from __future__ import annotations
from datetime import datetime


from fastapi import APIRouter, Path, Query

from ..models import (
    Exception as APIException,
    JobList,
    Results,
    StatusInfo,
    InlineResponse200,
)


DEFAULT_JOB_LIMIT = 1000

router: APIRouter = APIRouter(
    tags=["Jobs"],
)


@router.get(
    "/",
    response_model=JobList,
    responses={"404": {"model": APIException}},
)
def list_jobs(
    limit: int = Query(ge=1, default=DEFAULT_JOB_LIMIT),
    process_id: list[str] | None = Query(default=None),
    collection_id: list[str] | None = Query(default=None),
    item_id: list[str] | None = Query(default=None),
    start_datetime: datetime | None = None,
    end_datetime: datetime | None = None,
    parent_id: list[str] | None = Query(default=None),
) -> JobList | APIException:
    """
    retrieve the list of jobs.
    """
    pass


@router.get(
    "/{job_id}",
    response_model=StatusInfo,
    responses={
        "404": {"model": APIException},
        "500": {"model": APIException},
    },
)
def get_job_status(
    job_id: str = Path(..., alias="jobId"),
) -> StatusInfo | APIException:
    """
    retrieve the status of a job
    """
    pass


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
def get_job_result(job_id: str = Path(..., alias="jobId")) -> Results | APIException:
    """
    retrieve the result(s) of a job
    """
    pass


# TODO: model payload, use here for response
@router.get(
    "/{job_id}/payload",
    response_model=dict,
    responses={
        "404": {"model": APIException},
        "500": {"model": APIException},
    },
)
def get_job_payload(
    job_id: str = Path(..., alias="jobId"),
) -> dict | APIException:
    """
    retrieve the input payload of a job
    """
    pass


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
