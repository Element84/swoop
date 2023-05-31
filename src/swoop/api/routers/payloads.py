from __future__ import annotations

from asyncpg import Record
from buildpg import V, funcs, render
from fastapi import APIRouter, HTTPException, Path, Query, Request

from ..models import Action
from ..models import Exception as APIException
from ..models import (
    InlineResponse200,
    Link,
    PayloadDetails,
    PayloadInfo,
    PayloadList,
    StatusInfo,
)

DEFAULT_JOB_LIMIT = 1000

router: APIRouter = APIRouter(
    tags=["Payloads"],
)


def to_payload_details(record: Record) -> PayloadDetails:
    return PayloadDetails(
        payload_uuid=str(record["payload_uuid"]),
    )


def to_action(record) -> Action:
    return Action(
        action_uuid=str(record["action_uuid"]),
        action_type=record["action_type"],
        action_name=record["action_name"],
        handler_name=record["handler_name"],
        parent_uuid=str(record["parent_uuid"]),
        created_at=record["created_at"],
        priority=record["priority"],
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
    limit: int = Query(ge=1, default=DEFAULT_JOB_LIMIT),
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
                SELECT DISTINCT(c.payload_uuid)
                FROM swoop.item_payload i
                INNER JOIN swoop.payload_cache c
                ON c.payload_uuid = i.payload_uuid
                INNER JOIN swoop.action a
                ON c.payload_uuid = a.payload_uuid
                WHERE (:processes::text[] IS NULL OR :proc_where)
                AND (:collections::text[] IS NULL OR :coll_where)
                AND (:items::text[] IS NULL OR :item_where)
            """,
            processes=process_id,
            collections=collection_id,
            items=item_id,
            proc_where=proc_clause,
            coll_where=coll_clause,
            item_where=item_clause,
        )

        records = await conn.fetch(q, *p)

        if not records:
            raise HTTPException(
                status_code=404, detail="No payloads that match query parameters found"
            )

        if limit and limit < len(records):
            records = records[:limit]

        return PayloadList(
            payloads=[to_payload_details(pl) for pl in records],
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
    request: Request, payload_id: str
) -> PayloadInfo | APIException:
    """
    retrieve info for a payload
    """

    async with request.app.state.readpool.acquire() as conn:
        q, p = render(
            """
                    SELECT
                    *
                    FROM swoop.payload_cache c
                    INNER JOIN swoop.item_payload i
                    ON c.payload_uuid = i.payload_uuid
                    INNER JOIN swoop.action a
                    ON c.payload_uuid = a.payload_uuid
                    WHERE c.payload_uuid = :payload_id::uuid;
                """,
            payload_id=payload_id,
        )
        records = await conn.fetch(q, *p)

        if not records:
            raise HTTPException(
                status_code=404, detail="No payload that matches payload uuid found"
            )

        return PayloadInfo(
            payload_uuid=payload_id,
            payload_hash=str(records[0]["payload_hash"]),
            workflow_version=records[0]["workflow_version"],
            workflow_name=records[0]["workflow_name"],
            created_at=records[0]["created_at"],
            invalid_after=records[0]["invalid_after"],
            collections=list({record["collection"] for record in records}),
            items=list({record["item_id"] for record in records}),
            actions=[
                to_action(a)
                for a in list(
                    {record["action_uuid"]: record for record in records}.values()
                )
            ],
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
