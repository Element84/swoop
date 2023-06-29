from __future__ import annotations

from datetime import datetime
from enum import Enum
from uuid import UUID

from asyncpg import Record
from fastapi import Request
from pydantic import BaseModel

from swoop.api.models.shared import Link

status_dict = {
    "PENDING": "accepted",
    "QUEUED": "accepted",  # ?
    "RUNNING": "running",
    "SUCCESSFUL": "successful",
    "FAILED": "failed",
    "CANCELED": "dismissed",
    "TIMED_OUT": "failed",  # ?
    "UNKNOWN": "failed",  # ?
    "BACKOFF": "failed",  # ?
    "INVALID": "failed",  # ?
    "RETRIES_EXHAUSTED": "failed",  # ?
    #'INFO': '?' # ?
}


class SwoopStatusCode(str, Enum):
    pending = "PENDING"
    queued = "QUEUED"
    running = "RUNNING"
    successful = "SUCCESSFUL"
    failed = "FAILED"
    canceled = "CANCELED"
    timed_out = "TIMED_OUT"
    unknown = "UNKNOWN"
    backoff = "BACKOFF"
    invalid = "INVALID"
    retries_exhausted = "RETRIES_EXHAUSTED"


class StatusCode(str, Enum):
    accepted = "accepted"
    running = "running"
    successful = "successful"
    failed = "failed"
    dismissed = "dismissed"


class Type(Enum):
    process = "process"


class StatusInfo(BaseModel):
    processID: str
    type: Type
    jobID: UUID
    status: StatusCode
    message: str | None = None
    created: datetime | None = None
    started: datetime | None = None
    finished: datetime | None = None
    updated: datetime | None = None
    links: list[Link] = []

    def __init__(
        self,
        request: Request | None = None,
        payload_uuid: UUID | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        if request:
            url = str(
                request.url_for(
                    "get_job_status",
                    jobID=self.jobID,
                )
            )
            self.links += [
                Link.root_link(request),
                Link.self_link(
                    href=url,
                ),
                Link(
                    href=url + "/results",
                    # TODO: confirm rel
                    rel="results",
                    type="application/json",
                ),
                Link(
                    href=url + "/inputs",
                    # TODO: confirm rel
                    rel="inputs",
                    type="application/json",
                ),
                Link(
                    href=str(
                        request.url_for(
                            "get_process_description",
                            processID=self.processID,
                        )
                    ),
                    # TODO: confirm rel
                    rel="process",
                    type="application/json",
                ),
                Link(
                    href=str(
                        request.url_for(
                            "get_payload_cache_entry",
                            payloadID=payload_uuid,
                        )
                    ),
                    # TODO: confirm rel
                    rel="cache",
                    type="application/json",
                ),
            ]

    @classmethod
    def from_action_record(
        cls, record: Record, request: Request | None = None
    ) -> StatusInfo:
        return cls(
            processID=record["action_name"],
            type=Type("process"),
            jobID=str(record["action_uuid"]),
            status=StatusCode(status_dict[record["status"]]),
            created=record["created_at"],
            updated=record["last_update"],
            request=request,
            payload_uuid=record["payload_uuid"],
            started=record["started_at"],
            finished=record["last_update"]
            if status_dict[record["status"]] in ["successful", "failed", "dismissed"]
            else None,
        )


class JobList(BaseModel):
    jobs: list[StatusInfo]
    links: list[Link]
