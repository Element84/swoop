from __future__ import annotations

from uuid import UUID

from buildpg import V, funcs, render
from fastapi import APIRouter, HTTPException, Query, Request

from swoop.api.models.payloads import PayloadCacheEntry, PayloadCacheList
from swoop.api.models.shared import APIException, Link

DEFAULT_PAYLOAD_LIMIT = 1000

router: APIRouter = APIRouter(
    tags=["Payloads"],
)


@router.get(
    "/",
    response_model=PayloadCacheList,
    response_model_exclude_unset=True,
)
async def list_payload_cache(
    request: Request,
    limit: int = Query(ge=1, default=DEFAULT_PAYLOAD_LIMIT),
    processID: list[str] | None = Query(default=None),
) -> PayloadCacheList | APIException:
    """
    retrieve the list of payloads.
    """
    proc_clause = V("c.workflow_name") == funcs.any(processID)

    async with request.app.state.readpool.acquire() as conn:
        q, p = render(
            """
            SELECT
                c.payload_uuid as id,
                encode(c.payload_hash, 'base64') as "payloadHash",
                c.workflow_name as "processID",
                c.invalid_after as "invalidAfter"
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

        return PayloadCacheList(
            payloads=[
                PayloadCacheEntry.from_cache_record(record, request)
                for record in records
            ],
            links=[
                Link.root_link(request),
                Link.self_link(href=str(request.url)),
            ],
        )


@router.get(
    "/{payloadID}",
    response_model=PayloadCacheEntry,
    responses={
        "404": {"model": APIException},
        "500": {"model": APIException},
    },
    response_model_exclude_unset=True,
)
async def get_payload_cache_entry(
    request: Request,
    payloadID: UUID,
) -> PayloadCacheEntry | APIException:
    """
    retrieve info for a payload
    """

    async with request.app.state.readpool.acquire() as conn:
        q, p = render(
            """
            SELECT
                c.payload_uuid as id,
                encode(c.payload_hash, 'base64') as "payloadHash",
                c.workflow_name as "processID",
                c.invalid_after as "invalidAfter",
                array(
                    SELECT
                        action_uuid
                    FROM swoop.action
                    WHERE
                        payload_uuid = c.payload_uuid
                    ORDER BY created_at DESC
                ) AS "jobIDs"
            FROM swoop.payload_cache AS c
            WHERE
                c.payload_uuid = :payload_id::uuid
            """,
            payload_id=payloadID,
        )
        record = await conn.fetchrow(q, *p)

        if not record:
            raise HTTPException(
                status_code=404, detail="No payload that matches payload uuid found"
            )

        return PayloadCacheEntry.from_cache_record(record, request)
