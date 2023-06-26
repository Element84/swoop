from __future__ import annotations

from datetime import datetime
from enum import Enum

from asyncpg import Record
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


class StatusCode(Enum):
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
    jobID: str
    status: StatusCode
    message: str | None = None
    created: datetime | None = None
    started: datetime | None = None
    finished: datetime | None = None
    updated: datetime | None = None
    links: list[Link] | None = None

    @classmethod
    def from_action_record(cls, record: Record) -> StatusInfo:
        return cls(
            processID=record["action_name"],
            type=Type("process"),
            jobID=str(record["action_uuid"]),
            status=StatusCode(status_dict[record["status"]]),
            created=record["created_at"],
            updated=record["last_update"],
        )


class JobList(BaseModel):
    jobs: list[StatusInfo]
    links: list[Link]


class JobSummary(BaseModel):
    job_id: str | None = None
    href: str | None = None
    type: str | None = None
