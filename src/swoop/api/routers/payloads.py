from __future__ import annotations

from typing import Union

from fastapi import APIRouter, Path, Query

from ..models import (
    Exception as APIException,
    PayloadList,
    PayloadInfo,
    StatusInfo,
    InlineResponse200,
)


DEFAULT_JOB_LIMIT = 1000

router: APIRouter = APIRouter(
    tags=["Payloads"],
)


# The behavior here more or less requires we store payloads with a single
# unique key. That is, we need unique key in addition to the unique composite
# key formed by process_id and item collections and IDs.

@router.get(
    '/',
    response_model=PayloadList,
    responses={'404': {'model': APIException}},
)
def list_payloads(
    limit: int = Query(ge=1, default=DEFAULT_JOB_LIMIT),
    process_id: list[str] | None = Query(default=None),
    collection_id: list[str] | None = Query(default=None),
    item_id: list[str] | None = Query(default=None),
) -> Union[PayloadList, APIException]:
    """
    retrieve the list of payloads.
    """
    pass


@router.get(
    '/{payload_id}',
    response_model=PayloadInfo,
    responses={
        '404': {'model': APIException},
        '500': {'model': APIException},
    },
)
def get_job_status(
    payload_id: str = Path(..., alias='payloadId'),
) -> Union[PayloadInfo, APIException]:
    """
    retrieve info for a payload
    """
    pass


@router.post(
    '/{payload_id}/rerun',
    response_model=InlineResponse200,
    responses={
        '201': {'model': StatusInfo},
        '404': {'model': APIException},
        '500': {'model': APIException},
    },
)
def rerun_payload(
    payload_id: str = Path(..., alias='payloadId'),
) -> Union[InlineResponse200, StatusInfo, APIException]:
    """
    rerun a payload.
    """
    pass
