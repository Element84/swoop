from __future__ import annotations

from uuid import UUID

from asyncpg import Record
from buildpg import V, funcs, render
from fastapi import APIRouter, HTTPException, Query, Request

from swoop.api.models.jobs import JobSummary
from swoop.api.models.payloads import PayloadInfo, PayloadList, PayloadSummary
from swoop.api.models.shared import APIException, Link

DEFAULT_PAYLOAD_LIMIT = 1000

router: APIRouter = APIRouter(
    tags=["Payloads"],
)


def to_payload_summary(record: Record, request: Request) -> PayloadSummary:
    return PayloadSummary(
        payload_id=str(record["payload_uuid"]),
        href=str(
            request.url_for("get_payload_status", payloadID=record["payload_uuid"])
        ),
        type="payload",
    )


def to_job_summary(action_uuid: str, request: Request) -> JobSummary:
    return JobSummary(
        job_id=action_uuid,
        href=str(request.url_for("get_job_status", jobID=action_uuid)),
        type="job",
    )


# The behavior here more or less requires we store payloads with a single
# unique key. That is, we need unique key in addition to the unique composite
# key formed by process_id and item collections and IDs.


@router.get(
    "/",
    response_model=PayloadList,
    response_model_exclude_unset=True,
)
async def list_payloads(
    request: Request,
    limit: int = Query(ge=1, default=DEFAULT_PAYLOAD_LIMIT),
    processID: list[str] | None = Query(default=None),
) -> PayloadList | APIException:
    """
    retrieve the list of payloads.
    """
    proc_clause = V("c.workflow_name") == funcs.any(processID)

    async with request.app.state.readpool.acquire() as conn:
        q, p = render(
            """
            SELECT
                DISTINCT(c.payload_uuid)
            FROM swoop.payload_cache AS c
            WHERE
                (:processes::text[] IS NULL OR :proc_where)
            LIMIT :limit::integer
            """,
            processes=processID,
            proc_where=proc_clause,
            limit=limit,
        )

        records = await conn.fetch(q, *p)

        return PayloadList(
            payloads=[to_payload_summary(record, request) for record in records],
            links=[
                Link(
                    href="http://www.example.com",
                )
            ],
        )


@router.get(
    "/{payloadID}",
    response_model=PayloadInfo,
    responses={
        "404": {"model": APIException},
        "500": {"model": APIException},
    },
    response_model_exclude_unset=True,
)
async def get_payload_status(
    request: Request, payloadID: UUID
) -> PayloadInfo | APIException:
    """
    retrieve info for a payload
    """

    async with request.app.state.readpool.acquire() as conn:
        q, p = render(
            """
                SELECT
                c.payload_uuid,
                encode(c.payload_hash, 'base64') as payload_hash,
                c.workflow_name,
                c.created_at,
                c.invalid_after,
                array(
                    SELECT
                    action_uuid
                    FROM swoop.action
                    WHERE
                    payload_uuid = c.payload_uuid
                ) AS action_uuids
                FROM swoop.payload_cache AS c
                WHERE
                c.payload_uuid = :payload_id::uuid

            """,
            payload_id=payloadID,
        )
        records = await conn.fetch(q, *p)

        if not records:
            raise HTTPException(
                status_code=404, detail="No payload that matches payload uuid found"
            )

        actionids = {str(record) for record in records[0]["action_uuids"]}

        return PayloadInfo(
            payload_id=str(payloadID),
            payload_hash=records[0]["payload_hash"],
            workflow_name=records[0]["workflow_name"],
            created_at=records[0]["created_at"],
            invalid_after=records[0]["invalid_after"],
            jobs=[to_job_summary(a, request) for a in actionids],
        )
