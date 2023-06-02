from __future__ import annotations

from asyncpg import Record
from buildpg import V, funcs, render
from fastapi import APIRouter, HTTPException, Path, Query, Request

from ..models import Exception as APIException
from ..models import InlineResponse200, JobSummary, Link, StatusInfo
from ..models.payloads import Item, PayloadInfo, PayloadList, PayloadSummary

DEFAULT_PAYLOAD_LIMIT = 1000

router: APIRouter = APIRouter(
    tags=["Payloads"],
)


def to_payload_summary(record: Record, request: Request) -> PayloadSummary:
    return PayloadSummary(
        payload_id=str(record["payload_uuid"]),
        href=str(
            request.url_for("get_payload_status", payload_id=record["payload_uuid"])
        ),
        type="payload",
    )


def to_job_summary(action_uuid: str, request: Request) -> JobSummary:
    return JobSummary(
        job_id=action_uuid,
        href=str(request.url_for("get_job_status", job_id=action_uuid)),
        type="job",
    )


# The behavior here more or less requires we store payloads with a single
# unique key. That is, we need unique key in addition to the unique composite
# key formed by process_id and item collections and IDs.


@router.get(
    "/",
    response_model=PayloadList,
    responses={"404": {"model": APIException}},
)
async def list_payloads(
    request: Request,
    limit: int = Query(ge=1, default=DEFAULT_PAYLOAD_LIMIT),
    process_id: list[str] | None = Query(default=None),
    collection_id: list[str] | None = Query(default=None),
    item_id: list[str] | None = Query(default=None),
) -> PayloadList | APIException:
    """
    retrieve the list of payloads.
    """
    proc_clause = V("c.workflow_name") == funcs.any(process_id)
    coll_clause = V("i.collection") == funcs.any(collection_id)
    item_clause = V("i.item_id") == funcs.any(item_id)

    async with request.app.state.readpool.acquire() as conn:
        q, p = render(
            """
                WITH item_cache AS (
                    SELECT c.payload_uuid
                    FROM swoop.item_payload p
                    INNER JOIN swoop.payload_cache c
                    ON c.payload_uuid = p.payload_uuid
                    INNER JOIN swoop.input_item i
                    ON p.item_uuid = i.item_uuid
                    WHERE (:processes::text[] IS NULL OR :proc_where)
                    AND (:collections::text[] IS NULL OR :coll_where)
                    AND (:items::text[] IS NULL OR :item_where)
                    LIMIT :limit::integer
                )
                SELECT
                    DISTINCT(payload_uuid)
                FROM
                    item_cache;
            """,
            processes=process_id,
            collections=collection_id,
            items=item_id,
            proc_where=proc_clause,
            coll_where=coll_clause,
            item_where=item_clause,
            limit=limit,
        )

        records = await conn.fetch(q, *p)

        if not records:
            raise HTTPException(
                status_code=404, detail="No payloads that match query parameters found"
            )

        return PayloadList(
            payloads=[to_payload_summary(record, request) for record in records],
            links=[
                Link(
                    href="http://www.example.com",
                )
            ],
        )


@router.get(
    "/{payload_id}",
    response_model=PayloadInfo,
    responses={
        "404": {"model": APIException},
        "500": {"model": APIException},
    },
)
async def get_payload_status(
    request: Request, payload_id
) -> PayloadInfo | APIException:
    """
    retrieve info for a payload
    """

    async with request.app.state.readpool.acquire() as conn:
        q, p = render(
            """
                SELECT
                c.payload_uuid, payload_hash, workflow_version, workflow_name,
                c.created_at, invalid_after, item_id, collection, action_uuid
                FROM swoop.payload_cache c
                INNER JOIN swoop.item_payload p
                ON c.payload_uuid = p.payload_uuid
                INNER JOIN swoop.action a
                ON c.payload_uuid = a.payload_uuid
                INNER JOIN swoop.input_item i
                ON p.item_uuid = i.item_uuid
                WHERE c.payload_uuid = :payload_id::uuid;
            """,
            payload_id=payload_id,
        )
        records = await conn.fetch(q, *p)

        if not records:
            raise HTTPException(
                status_code=404, detail="No payload that matches payload uuid found"
            )

        actionids = {str(record["action_uuid"]) for record in records}
        item_coll = list(
            {(record["item_id"], record["collection"]) for record in records}
        )

        return PayloadInfo(
            payload_id=payload_id,
            payload_hash=str(records[0]["payload_hash"]),
            workflow_version=records[0]["workflow_version"],
            workflow_name=records[0]["workflow_name"],
            created_at=records[0]["created_at"],
            invalid_after=records[0]["invalid_after"],
            items=[Item(item_id=i[0], collection=i[1]) for i in item_coll],
            jobs=[to_job_summary(a, request) for a in actionids],
        )


@router.post(
    "/{payload_id}/rerun",
    response_model=InlineResponse200,
    responses={
        "201": {"model": StatusInfo},
        "404": {"model": APIException},
        "500": {"model": APIException},
    },
)
def rerun_payload(
    payload_id: str = Path(..., alias="payloadId"),
) -> InlineResponse200 | StatusInfo | APIException:
    """
    rerun a payload.
    """
    pass
