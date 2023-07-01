from __future__ import annotations

from uuid import UUID

from buildpg import V, funcs, render
from fastapi import APIRouter, HTTPException, Query, Request

from swoop.api.models.payloads import PayloadCacheEntry, PayloadCacheList
from swoop.api.models.shared import APIException, Link
from swoop.api.models.workflows import Execute, Workflows

DEFAULT_PAYLOAD_LIMIT = 1000

router: APIRouter = APIRouter(
    tags=["Payloads"],
)


@router.get(
    "/",
    response_model=PayloadCacheList,
    response_model_exclude_unset=True,
)
async def list_input_payload_cache_entries(
    request: Request,
    limit: int = Query(ge=1, default=DEFAULT_PAYLOAD_LIMIT),
    processID: list[str] | None = Query(default=None),
) -> PayloadCacheList | APIException:
    """
    Returns a list of cached input payloads and the association with workflow executions
    """
    proc_clause = V("c.workflow_name") == funcs.any(processID)

    async with request.app.state.readpool.acquire() as conn:
        q, p = render(
            """
            SELECT
                c.payload_uuid as id,
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


async def get_payload_cache_entry_from_db(
    request: Request,
    payload_uuid: UUID,
) -> PayloadCacheEntry:
    async with request.app.state.readpool.acquire() as conn:
        q, p = render(
            """
            SELECT
                c.payload_uuid as id,
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
            payload_id=payload_uuid,
        )
        record = await conn.fetchrow(q, *p)

    if not record:
        raise HTTPException(
            status_code=404, detail="No payload that matches payload uuid found"
        )

    return PayloadCacheEntry.from_cache_record(record, request)


@router.get(
    "/{payloadID}",
    response_model=PayloadCacheEntry,
    responses={
        "404": {"model": APIException},
        "500": {"model": APIException},
    },
    response_model_exclude_unset=True,
)
async def get_input_payload_cache_entry(
    request: Request,
    payloadID: UUID,
) -> PayloadCacheEntry | APIException:
    """
    Retrieve details of cached input payload by payloadID
    """
    return await get_payload_cache_entry_from_db(request, payloadID)


@router.post(
    "/",
    response_model=PayloadCacheEntry,
    responses={
        "404": {"model": APIException},
        "500": {"model": APIException},
    },
    response_model_exclude_unset=True,
)
async def retrieve_payload_cache_entry_by_payload_input(
    request: Request,
    body: Execute,
) -> PayloadCacheEntry | APIException:
    """
    Retrieves details of cached input payload via a payload hash lookup
    """

    payload = body.inputs.payload
    workflows: Workflows = request.app.state.workflows

    try:
        workflow = workflows[payload.current_process_definition().workflow]
    except KeyError:
        raise HTTPException(status_code=404, detail="Workflow not found")

    payload_uuid = workflow.generate_payload_uuid(payload)
    return await get_payload_cache_entry_from_db(request, payload_uuid)


@router.post(
    "/{payloadID}/invalidate",
    response_model=None,
    responses={
        "404": {"model": APIException},
        "422": {"model": APIException},
        "500": {"model": APIException},
    },
    response_model_exclude_unset=True,
)
async def update_input_payload_cache_entry_invalidation(
    request: Request,
    payloadID: UUID,
    body: PayloadCacheEntry,
) -> APIException:
    """
    Updates input payload cache invalidation
    """

    if body.id != payloadID:
        raise HTTPException(
            status_code=422, detail="Input id does not match payload ID"
        )

    response = ""
    if body.invalidNow:
        async with request.app.state.readpool.acquire() as conn:
            q, p = render(
                """
                UPDATE
                    swoop.payload_cache
                SET invalid_after=now()
                WHERE
                    payload_uuid=:payload_id::uuid;
                """,
                payload_id=payloadID,
            )
            response = await conn.execute(q, *p)

    else:
        async with request.app.state.readpool.acquire() as conn:
            q, p = render(
                """
                UPDATE
                    swoop.payload_cache
                SET invalid_after=:invalid_after::TIMESTAMPTZ
                WHERE
                    payload_uuid=:payload_id::uuid;
                """,
                payload_id=payloadID,
                invalid_after=body.invalidAfter,
            )
            response = await conn.execute(q, *p)

    if not response or response == "UPDATE 0":
        raise HTTPException(status_code=404, detail="Payload ID not found")

    return response
