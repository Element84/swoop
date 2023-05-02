from __future__ import annotations
from datetime import datetime
from pydantic import create_model
from itertools import groupby
from asyncpg import Record
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
#   start_datetime -> event.event_time = {start_datetime}, and event.status = 'RUNNING'
#   end_datetime -> event.event_time = {end_datetime}, and event.status = 'COMPLETED'
#   parent_id -> action.parent_uuid
#   job_id -> action.action_uuid


status_dict = {
    'PENDING': 'accepted',
    'QUEUED': 'running', # ?
    'RUNNING': 'running',
    'SUCCESSFUL': 'successful',
    'FAILED': 'failed',
    'CANCELED': 'dismissed',
    'TIMED_OUT': 'failed', # ?
    'UNKNOWN': 'failed', # ?
    'BACKOFF': 'failed', # ?
    'INVALID': 'failed', # ?
    'RETRIES_EXHAUSTED': 'failed', # ?
    #'INFO': '?' # ?
}


def to_status_info(records: list[Record]) -> StatusInfo:
    latest = max(records, key=lambda rec: rec['created_at'])

    return StatusInfo(
        processID=latest['action_name'],
        type='process',
        jobID=str(latest['action_uuid']),
        status=status_dict[latest['status']],
        # created = 
        # started = 
        # finished =
        updated=latest['event_time'],
        parentID=latest['parent_uuid']
    )

def group_records(records: list[Record]) -> list[list[Record]]:
    record_groups = groupby(records, lambda r: r['action_uuid'])

    results = []
    for element, group in record_groups:
        results.append(list(group))

    return results

def job_query(where, limit) -> str:
    return """
        SELECT 
        *
        FROM swoop.action a
        INNER JOIN swoop.event e 
        ON e.action_uuid = a.action_uuid
        WHERE a.action_type = 'workflow' {w} {l} ;
        """.format(w=where, l=limit)


def build_query(params, limit=None) -> JobList:
    sql_where = ''
    sql_limit = f"LIMIT {limit}" if limit else ''

    if len(params) > 0:

        for key,value in params.items():
            
            if key == 'process_id':
                key = 'a.action_name'

            if key == 'parent_id':
                key = 'a.parent_uuid'

            if key == 'job_id':
                key = 'a.action_uuid'

            if key == 'start_datetime':
                key = 'e.event_time'
                sql_where += "AND e.status = 'RUNNING' "

            if key == 'end_datetime':
                key = 'e.event_time'
                sql_where += "AND e.status = 'COMPLETED' "

            if ',' in value:
                quoted = value.replace(",", "', '")
                sql_where += f"AND {key} in ('{quoted}') " # List
            else:
                sql_where += f"AND {key} = '{value}' " # Single Value

    sql = job_query(sql_where, sql_limit)

    #print (sql)
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
    sql = build_query(params.dict(exclude_none=True), limit)
    async with request.app.state.readpool.acquire() as conn:
        record_groups = group_records(await conn.fetch(sql))

        statusinfo_list = []

        for group in record_groups:
            statusinfo_list.append(to_status_info(group))

        return JobList(
            jobs=statusinfo_list,
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
        sql = build_query({ 'job_id': job_id })
        records = await conn.fetch(sql)

        if not records:
            raise HTTPException(status_code=404, detail="Job not found")

        return to_status_info(records)


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
        sql = build_query({ 'job_id': job_id })
        records = await conn.fetch(sql)

        if not records:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # TODO - Fix this with correct Results data
        #return Results({})
        return {
            "example": "example results"
        }


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
        sql = """
            SELECT 1 FROM swoop.action WHERE action_type = 'workflow' 
            AND action_uuid = '{j}';
            """.format(j = job_id)
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
