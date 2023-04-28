from __future__ import annotations
from datetime import datetime
from pydantic import create_model

from fastapi import APIRouter, Path, Query, Request, Depends, HTTPException

from ..models import (
    Exception as APIException,
    JobList,
    Link,
    Results,
    StatusInfo,
    InlineResponse200,
)


DEFAULT_JOB_LIMIT = 1000

router: APIRouter = APIRouter(
    tags=["Jobs"],
)


# Put your query arguments in this dict
list_jobs_params = {
    'process_id': (str, None),
    'collection_id': (str, None),
    'item_id': (str, None),
    'start_datetime': (datetime, None),
    'end_datetime': (datetime, None),
    'parent_id': (str, None),
    'action_type': (str, 'workflow')
}
list_jobs_query_model = create_model("Query", **list_jobs_params)

### TODO
# Update StatusInfo getters(?) to calculate the status based on the Thread info 
# Transform query params into correct query ... some params apply to 'action', some to 'thread'
#   join where:
#     action_uuid match
#     created_at is latest
#   present 

# class StatusInfo(BaseModel):
#     processID: str | None = None   
#     type: Type
#     jobID: str
#     status: StatusCode
#     message: str | None = None
#     created: datetime | None = None
#     started: datetime | None = None
#     finished: datetime | None = None
#     updated: datetime | None = None
#     progress: conint(ge=0, le=100) | None = None
#     links: list[Link] | None = None
#     parentID: str | None = None

def build_query(table, params, limit) -> JobList:
    params_dict = params.dict(exclude_none=True)
    sql = f'SELECT * FROM {table}'

    if len(params_dict) > 0:
        sql += ' WHERE'

        delimiter = ''
        for key,value in params_dict.items():
            if ',' in value:
                quoted = value.replace(",", "', '")
                sql += f"{delimiter} {key} in ('{quoted}')" # List
            else:
                sql += f"{delimiter} {key} = '{value}'" # Single Value
            delimiter = ' AND'

    if limit:
        sql += f" LIMIT {limit}"
    sql += ';'

    #print (sql)
    return sql

@router.get(
    "/",
    response_model=JobList,
    responses={"404": {"model": APIException}},
)
async def list_jobs(
    request: Request,
    limit: int = Query(ge=1, default=DEFAULT_JOB_LIMIT),
    params: list_jobs_query_model = Depends()
) -> JobList | APIException:
    """
    retrieve the list of jobs.
    """
    sql = build_query('swoop.action', params, limit)
    async with request.app.state.readpool.acquire() as conn:
        return JobList(
            jobs=[
                StatusInfo(
                    type='process',
                    jobID='jobid',
                    status='running'
                )
            ],
            links=[
                Link(
                    href='http://www.example.com',
                )
            ]
        )


@router.get(
    "/{job_id}",
    response_model=StatusInfo,
    responses={
        "404": {"model": APIException},
        "500": {"model": APIException},
    },
)
async def get_job_status(
    request: Request,
    job_id
) -> StatusInfo | APIException:
    """
    retrieve the status of a job
    """
    async with request.app.state.readpool.acquire() as conn:
        sql = f"SELECT 1 FROM swoop.action WHERE action_type = 'workflow' AND action_uuid = '{job_id}';"
        job = await conn.fetch(sql)

        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return StatusInfo(
            type='process',
            jobID='jobid',
            status='running'
        )


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
        sql = f"SELECT 1 FROM swoop.action WHERE action_type = 'workflow' AND action_uuid = '{job_id}';"
        job = await conn.fetch(sql)

        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # TODO - This isn't valid. I don't understand the Results model schema
        #        Fix this, and then uncomment the test for it
        return Results({})


# TODO: model payload, use here for response
@router.get(
    "/{job_id}/payload",
    response_model=dict,
    responses={
        "404": {"model": APIException},
        "500": {"model": APIException},
    },
)
async def get_job_payload(
    request: Request,
    job_id
) -> dict | APIException:
    """
    retrieve the input payload of a job
    """
    async with request.app.state.readpool.acquire() as conn:
        sql = f"SELECT 1 FROM swoop.action WHERE action_type = 'workflow' AND action_uuid = '{job_id}';"
        job = await conn.fetch(sql)

        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return {
            "example": "example payload"
        }


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
