from __future__ import annotations

from enum import Enum
from typing import Any

from fastapi import Request
from jsonschema import Draft202012Validator
from pydantic import AnyUrl, BaseModel, Field, PrivateAttr, RootModel, model_validator


class APIException(BaseModel, extra="allow"):
    status: int
    detail: str
    type: str | None = None
    title: str | None = None
    instance: str | None = None


class Link(BaseModel):
    href: AnyUrl
    rel: str
    type: str
    hreflang: str | None = None
    title: str | None = None

    # redefining init is a hack to get str type to validate for `href`,
    # as str is ultimately coerced into an AnyUrl automatically anyway
    def __init__(self, href: AnyUrl | str, **kwargs):
        super().__init__(href=href, **kwargs)

    @classmethod
    def root_link(cls, request: Request) -> Link:
        return cls(
            href=str(request.url_for("get_landing_page")),
            rel="root",
            type="application/json",
        )

    @classmethod
    def self_link(cls, *, href: AnyUrl | str, **kwargs) -> Link:
        attrs = dict(
            href=href,
            rel="self",
            type="application/json",
        )
        attrs.update(**kwargs)
        return cls(**attrs)

    @classmethod
    def next_link(cls, *, href: AnyUrl | str, **kwargs) -> Link:
        attrs = dict(
            href=href,
            rel="next",
            type="application/json",
        )
        attrs.update(**kwargs)
        return cls(**attrs)


class TransmissionMode(str, Enum):
    value = "value"
    reference = "reference"


class Format(BaseModel):
    mediaType: str | None = None
    encoding: str | None = None
    schema_: str | dict[str, Any] | None = Field(None, alias="schema")


class Metadata(BaseModel):
    title: str | None = None
    role: str | None = None
    href: str | None = None


class AdditionalParameter(BaseModel):
    name: str
    value: list[str | float | int | list[dict[str, Any]] | dict[str, Any]]


class Reference(BaseModel, extra="forbid"):
    field_ref: str = Field(..., alias="$ref")


BinaryInputValue = RootModel[str]


class Crs(str, Enum):
    OGC_1_3_CRS84 = "http://www.opengis.net/def/crs/OGC/1.3/CRS84"
    OGC_0_CRS84h = "http://www.opengis.net/def/crs/OGC/0/CRS84h"


class Bbox(BaseModel):
    bbox: list[float]
    crs: Crs | None = Crs.OGC_1_3_CRS84


class Output(BaseModel):
    format: Format | None = None
    transmissionMode: TransmissionMode = TransmissionMode.value


class AdditionalParameters(Metadata):
    parameters: list[AdditionalParameter] | None = None


class DescriptionType(BaseModel):
    title: str | None = None
    description: str | None = None
    keywords: list[str] | None = None
    metadata: list[Metadata] | None = None
    additionalParameters: AdditionalParameters | None = None


InputValueNoObject = RootModel[
    str | float | int | bool | list[str] | BinaryInputValue | Bbox
]


InputValue = RootModel[InputValueNoObject | dict[str, Any]]


class QualifiedInputValue(Format):
    value: InputValue


InlineOrRefData = RootModel[InputValueNoObject | QualifiedInputValue | Link]


Results = RootModel[dict[str, InlineOrRefData] | None]


InlineResponse200 = RootModel[
    str | float | int | dict[str, Any] | list[dict[str, Any]] | bool | bytes | Results
]


class Schema(RootModel[dict[str, Any]]):
    _validator: Draft202012Validator = PrivateAttr()

    @model_validator(mode="before")
    @classmethod
    def check_schema(cls, data: Any) -> Any:
        Draft202012Validator.check_schema(data)
        return data

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._validator = Draft202012Validator(kwargs)

    def run_validator(self, data: dict[str, Any]):
        self._validator.validate(data)
