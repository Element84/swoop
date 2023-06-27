from __future__ import annotations

from datetime import datetime
from uuid import UUID

from asyncpg import Record
from fastapi import Request
from pydantic import BaseModel

from swoop.api.models.shared import Link


class PayloadCacheEntry(BaseModel):
    id: UUID
    payloadHash: str
    processID: str
    invalidAfter: datetime | None
    links: list[Link] = []

    def __init__(
        self,
        request: Request | None = None,
        jobIDs: list[UUID] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        if request:
            self.links += [
                Link.root_link(request),
                Link.self_link(
                    href=str(
                        request.url_for("get_payload_cache_entry", payloadID=self.id)
                    ),
                ),
            ]

        if request and jobIDs:
            for job_id in jobIDs:
                self.links.append(
                    Link(
                        href=str(request.url_for("get_job_status", jobID=job_id)),
                        type="application/json",
                        # TODO: verify appropriate rel
                        rel="job",
                    )
                )

    @classmethod
    def from_cache_record(
        cls,
        record: Record,
        request: Request | None = None,
    ):
        return cls(request=request, **record)


class PayloadCacheList(BaseModel):
    payloads: list[PayloadCacheEntry]
    links: list[Link]

    def __init__(self, request: Request | None = None, **kwargs) -> None:
        super().__init__(**kwargs)

        if request:
            self.links += [
                Link.root_link(request),
                Link.self_link(href=str(request.url)),
            ]
