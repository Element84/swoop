from __future__ import annotations

from datetime import datetime
from enum import Enum
from uuid import UUID

from asyncpg import Record
from fastapi import Request
from pydantic import BaseModel

from swoop.api.models.shared import Link


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

    @classmethod
    def terminal_states(cls):
        return (
            cls.successful,
            cls.failed,
            cls.canceled,
            cls.timed_out,
            cls.invalid,
            cls.retries_exhausted,
        )

    @classmethod
    def duration_states(cls):
        return cls.terminal_states() + (cls.running, cls.queued)

    @property
    def is_terminal(self):
        return self in self.terminal_states()


class StatusCode(str, Enum):
    accepted = "accepted"
    running = "running"
    successful = "successful"
    failed = "failed"
    dismissed = "dismissed"

    @classmethod
    def from_swoop_status(cls, swoop_status: SwoopStatusCode):
        status_dict = {
            SwoopStatusCode.pending: cls.accepted,
            SwoopStatusCode.queued: cls.accepted,
            SwoopStatusCode.running: cls.running,
            SwoopStatusCode.successful: cls.successful,
            SwoopStatusCode.failed: cls.failed,
            SwoopStatusCode.canceled: cls.dismissed,
            SwoopStatusCode.timed_out: cls.failed,
            SwoopStatusCode.unknown: cls.failed,
            SwoopStatusCode.backoff: cls.failed,
            SwoopStatusCode.invalid: cls.failed,
            SwoopStatusCode.retries_exhausted: cls.failed,
        }

        return status_dict[swoop_status]

    @classmethod
    def terminal_states(cls):
        return (
            cls.successful,
            cls.failed,
            cls.dismissed,
        )

    @property
    def is_terminal(self):
        return self in self.terminal_states()


class Type(str, Enum):
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
                    "get_workflow_execution_details",
                    jobID=self.jobID,
                )
            )
            self.links += [
                Link.root_link(request),
                Link.self_link(
                    href=url,
                ),
                Link(
                    href=str(
                        request.url_for(
                            "get_workflow_description",
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
                            "get_input_payload_cache_entry",
                            payloadID=payload_uuid,
                        )
                    ),
                    # TODO: confirm rel
                    rel="cache",
                    type="application/json",
                ),
                Link(
                    href=url + "/inputs",
                    # TODO: confirm rel
                    rel="inputs",
                    type="application/json",
                ),
            ]

            if kwargs.get("status", None) == StatusCode.successful:
                self.links += (
                    Link(
                        href=url + "/results",
                        # TODO: confirm rel
                        rel="results",
                        type="application/json",
                    ),
                )

    @classmethod
    def from_action_record(
        cls, record: Record, request: Request | None = None
    ) -> StatusInfo:
        status = StatusCode.from_swoop_status(record["status"])
        return cls(
            processID=record["action_name"],
            type=Type("process"),
            jobID=str(record["action_uuid"]),
            status=status,
            created=record["created_at"],
            updated=record["last_update"],
            request=request,
            payload_uuid=record["payload_uuid"],
            started=record["started_at"],
            finished=record["last_update"] if status.is_terminal else None,
        )


class JobList(BaseModel):
    jobs: list[StatusInfo]
    links: list[Link]
