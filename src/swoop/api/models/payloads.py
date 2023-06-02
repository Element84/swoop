from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from ..models import JobSummary, Link


class Item(BaseModel):
    item_id: str | None = None
    collection: str | None = None


class PayloadSummary(BaseModel):
    payload_id: str | None = None
    href: str | None = None
    type: str | None = None


class PayloadList(BaseModel):
    payloads: list[PayloadSummary]
    links: list[Link]


class PayloadInfo(BaseModel):
    payload_id: str | None = None
    payload_hash: bytes | None = None
    workflow_version: int | None = None
    workflow_name: str | None = None
    created_at: datetime | None = None
    invalid_after: datetime | None = None
    items: list[Item] | None = None
    jobs: list[JobSummary] | None = None
