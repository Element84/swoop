from __future__ import annotations

from typing import Any
from uuid import UUID

from buildpg import V, funcs, render
from fastapi import APIRouter, HTTPException, Query, Request, Response

from swoop.api.models.payloads import Invalid, PayloadCacheEntry, PayloadCacheList
from swoop.api.models.shared import APIException, Link
from swoop.api.models.workflows import Payload, Workflows

DEFAULT_PAYLOAD_LIMIT = 1000

router: APIRouter = APIRouter(
    tags=["Payloads"],
)


@router.get(
    "",
    response_model=PayloadCacheList,
    response_model_exclude_unset=True,
)
async def list_input_payload_cache_entries(
    request: Request,
    limit: int = Query(ge=1, default=DEFAULT_PAYLOAD_LIMIT),
    processID: list[str] | None = Query(default=None),
    lastID: UUID | None = None,
) -> PayloadCacheList | APIException:
    """
    Returns a list of cached input payloads and the association with workflow executions
    """
    proc_clause = V("workflow_name") == funcs.any(processID)

    async with request.app.state.readpool.acquire() as conn:
        q, p = render(
            """
            SELECT
                payload_uuid as id,
                workflow_name as "processID",
                invalid_after as "invalidAfter"
            FROM swoop.payload_cache
            WHERE
                (:processes::text[] IS NULL OR :proc_where)
                AND
                (:last::uuid IS NULL OR payload_uuid > :last)
            ORDER BY payload_uuid
            LIMIT :limit
            """,
            processes=processID,
            proc_where=proc_clause,
            last=lastID,
            limit=limit + 1,
        )

        records = await conn.fetch(q, *p)

        links = [
            Link.root_link(request),
            Link.self_link(href=str(request.url)),
        ]

        if len(records) > limit:
            records.pop(-1)
            lastID = records[-1]["id"]
            links.append(
                Link.next_link(
                    href=str(request.url.include_query_params(lastID=lastID)),
                ),
            )

        return PayloadCacheList(
            payloads=[
                PayloadCacheEntry.from_cache_record(record, request)
                for record in records
            ],
            links=links,
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
    # TODO: what about the Execute model here?
    body: dict[str, Any],
) -> PayloadCacheEntry | APIException:
    """
    Retrieves details of cached input payload via a payload hash lookup
    """

    inputs = body.get("inputs", None)

    if inputs is None:
        raise HTTPException(status_code=422, detail="inputs required")

    payload = inputs.get("payload", {}).get("value")

    validated = Payload(**payload)
    workflow_name = validated.current_process_definition().workflow

    workflows: Workflows = request.app.state.workflows

    try:
        workflow = workflows[workflow_name]
    except KeyError:
        raise HTTPException(status_code=404, detail="Workflow not found")

    workflow.validate_inputs(inputs)

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
    body: Invalid,
) -> Response | APIException:
    """
    Set invalidAfter property on a payload cache entry
    """
    async with request.app.state.readpool.acquire() as conn:
        q, p = render(
            """
            UPDATE
                swoop.payload_cache
                SET invalid_after = :invalid_after::timestamptz
            WHERE
                payload_uuid=:payload_id::uuid;
            """,
            payload_id=payloadID,
            invalid_after=body.invalidAfter,
        )
        response = await conn.execute(q, *p)

    if not response or response == "UPDATE 0":
        raise HTTPException(status_code=404, detail="Payload ID not found")

    return Response()
