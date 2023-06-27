from __future__ import annotations

from enum import Enum
from typing import Any

from fastapi import Request
from pydantic import AnyUrl, BaseModel, Extra, Field, PositiveFloat, conint


class APIException(BaseModel):
    class Config:
        extra = Extra.allow

    type: str
    title: str | None = None
    status: int | None = None
    detail: str | None = None
    instance: str | None = None


class Link(BaseModel):
    href: AnyUrl
    rel: str = Field(example="service")
    type: str = Field(example="application/json")
    hreflang: str | None = None
    title: str | None = None

    # redefining init is a hack to get str type to validate for `href`,
    # as str is ultimately coerced into an AnyUrl automatically anyway
    def __init__(self, href: AnyUrl | str, **kwargs):
        super().__init__(href=href, **kwargs)

    def dict(self, *args, **kwargs):
        # we force exclude_unset here to ensure undefined fields are not
        # included in the response, specifically for links specified in
        # the workflow config, where using `parse_obj()` doesn't allow us
        # to specify this option in any other way
        kwargs["exclude_unset"] = True
        return super().dict(*args, **kwargs)

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


class Subscriber(BaseModel):
    successUri: AnyUrl | None = None
    inProgressUri: AnyUrl | None = None
    failedUri: AnyUrl | None = None


class TransmissionMode(Enum):
    value = "value"
    reference = "reference"


class Type1(Enum):
    array = "array"
    boolean = "boolean"
    integer = "integer"
    number = "number"
    object = "object"
    string = "string"


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


class Reference(BaseModel):
    field_ref: str = Field(..., alias="$ref")


class BinaryInputValue(BaseModel):
    __root__: str


class Crs(Enum):
    http___www_opengis_net_def_crs_OGC_1_3_CRS84 = (
        "http://www.opengis.net/def/crs/OGC/1.3/CRS84"
    )
    http___www_opengis_net_def_crs_OGC_0_CRS84h = (
        "http://www.opengis.net/def/crs/OGC/0/CRS84h"
    )


class Bbox(BaseModel):
    bbox: list[float]
    crs: Crs | None = "http://www.opengis.net/def/crs/OGC/1.3/CRS84"


class Output(BaseModel):
    format: Format | None = None
    transmissionMode: TransmissionMode | None = "value"


class AdditionalParameters(Metadata):
    parameters: list[AdditionalParameter] | None = None


class DescriptionType(BaseModel):
    title: str | None = None
    description: str | None = None
    keywords: list[str] | None = None
    metadata: list[Metadata] | None = None
    additionalParameters: AdditionalParameters | None = None


class InputValueNoObject(BaseModel):
    __root__: str | float | int | bool | list[str] | BinaryInputValue | Bbox


class InputValue(BaseModel):
    __root__: InputValueNoObject | dict[str, Any]


class QualifiedInputValue(Format):
    value: InputValue


class InlineOrRefData(BaseModel):
    __root__: InputValueNoObject | QualifiedInputValue | Link


class Results(BaseModel):
    # TODO: This becomes the schema of the workflow output
    __root__: dict[str, InlineOrRefData] | None = None


class InlineResponse200(BaseModel):
    __root__: (
        str
        | float
        | int
        | dict[str, Any]
        | list[dict[str, Any]]
        | bool
        | bytes
        | Results
    )


class Schema(BaseModel):
    __root__: Reference | SchemaItem


class SchemaItem(BaseModel):
    class Config:
        extra = Extra.forbid

    title: str | None = None
    multipleOf: PositiveFloat | None = None
    maximum: float | None = None
    exclusiveMaximum: bool | None = False
    minimum: float | None = None
    exclusiveMinimum: bool | None = False
    maxLength: conint(ge=0) | None = None
    minLength: conint(ge=0) | None = 0
    pattern: str | None = None
    maxItems: conint(ge=0) | None = None
    minItems: conint(ge=0) | None = 0
    uniqueItems: bool | None = False
    maxProperties: conint(ge=0) | None = None
    minProperties: conint(ge=0) | None = 0
    required: list[str] | None = Field(None, min_items=1, unique_items=True)
    enum: list[dict[str, Any]] | None = Field(None, min_items=1, unique_items=False)
    type: Type1 | None = None
    not_: Schema | Reference | None = Field(None, alias="not")
    allOf: list[Schema | Reference] | None = None
    oneOf: list[Schema | Reference] | None = None
    anyOf: list[Schema | Reference] | None = None
    items: Schema | Reference | None = None
    properties: dict[str, Schema | Reference] | None = None
    additionalProperties: Schema | Reference | bool | None = True
    description: str | None = None
    format: str | None = None
    default: dict[str, Any] | None = None
    nullable: bool | None = False
    readOnly: bool | None = False
    writeOnly: bool | None = False
    example: dict[str, Any] | None = None
    deprecated: bool | None = False
    contentMediaType: str | None = None
    contentEncoding: str | None = None
    contentSchema: str | None = None


Schema.update_forward_refs()
