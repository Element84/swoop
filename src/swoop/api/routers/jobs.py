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


### Query Param Mapping Guide
# 
# Job requests contain params that may not directly map to a DB field.
# Below is an explanation of what each query param maps to.
#
# A join between the 'action' and 'thread' tables is necessary before filtering
# by certain params, and generating a StatusInfo response object.
#
#   process_id -> action.action_name
#   start_datetime -> thread.created_at = {start_datetime}, and thread.status = 'RUNNING'
#   end_datetime -> thread.created_at = {end_datetime}, and thread.status = 'COMPLETED'
#   parent_id -> action.parent_uuid
#   job_id -> action.action_uuid


def join_query() -> str:
    return """
        SELECT 
        *
        FROM swoop.action a
        INNER JOIN swoop.thread t 
        ON t.action_uuid = a.action_uuid
        WHERE a.action_type = 'workflow'  # hmmm ... need to insert more WHERE args here
        GROUP BY a.action_uuid
        """
    ### Do we want to rename anything as part of SELECT?
    # a.action_name AS processID
    # a.action_uuid AS jobID
    # a.parent_uuid AS parentID

def build_query(params, limit) -> JobList:
    params_dict = params.dict(exclude_none=True)
    sql = join_query()

    if len(params_dict) > 0:

        for key,value in params_dict.items():
            
            if key == 'process_id':
                key = f'a.action_name'

            if key == 'parent_id':
                key = f'a.parent_uuid'

            if key == 'job_id':
                key = f'a.action_uuid'

            if key == 'start_datetime':
                key = f't.created_at'
                sql += " AND t.status = 'RUNNING'"

            if key == 'end_datetime':
                key = f't.created_at'
                sql += " AND t.status = 'COMPLETED'"

            if ',' in value:
                quoted = value.replace(",", "', '")
                sql += f" AND {key} in ('{quoted}')" # List
            else:
                sql += f" AND {key} = '{value}'" # Single Value

    if limit:
        sql += f" LIMIT {limit}"
    sql += ';'

    # call build_query here ... pass it {where} and {limit}, insert them

    print (sql)
    return sql


params = {
    'process_id': (str, None),
    #'collection_id': (str, None),  # TODO - possibly named just 'collection'
    #'item_id': (str, None),        # TODO
    'start_datetime': (datetime, None),
    'end_datetime': (datetime, None),
    'parent_id': (str, None)
}
jobs_list_params = create_model("Query", **params)


@router.get(
    "/",
    response_model=JobList,
    responses={"404": {"model": APIException}},
)
async def list_jobs(
    request: Request,
    limit: int = Query(ge=1, default=DEFAULT_JOB_LIMIT),
    params: jobs_list_params = Depends()
) -> JobList | APIException:
    """
    retrieve the list of jobs.
    """
    sql = build_query(params, limit)
    async with request.app.state.readpool.acquire() as conn:
        jobs = await conn.fetch(sql)

        # jobs -> [ <Record>, <Record>, <Record> ]
        # we probably want: per a.action_uuid, the latest by (t.created_at or t.last_update) ?


# TODO delete me
#     class StatusInfo(BaseModel):
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

        print (jobs)
        # TODO ... transform jobs into StatusInfo objects
        #   either do this in the StatusInfo constructor, or use 'as' in the query
        #   consider the other /jobs requests ... which option would they share best?
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
        
        # TODO complete this
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
        
        # TODO - implement this later
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
