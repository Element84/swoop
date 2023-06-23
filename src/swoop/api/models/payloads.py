from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from swoop.api.models.jobs import JobSummary
from swoop.api.models.shared import Link


class PayloadSummary(BaseModel):
    payload_id: str | None = None
    href: str | None = None
    type: str | None = None


class PayloadList(BaseModel):
    payloads: list[PayloadSummary]
    links: list[Link]


class PayloadInfo(BaseModel):
    payload_id: str
    payload_hash: str
    workflow_name: str
    created_at: datetime
    invalid_after: datetime | None
    jobs: list[JobSummary]
