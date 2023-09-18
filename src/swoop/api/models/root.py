from __future__ import annotations

from pydantic import BaseModel, Field

from swoop.api.models.shared import Link


class ConfClasses(BaseModel):
    conformsTo: list[str]
    links: list[Link]


class LandingPage(BaseModel):
    title: str | None = Field(None, example="Example processing server")
    description: str | None = Field(
        None, example="Example server implementing the OGC API - Processes 1.0 Standard"
    )
    links: list[Link]
