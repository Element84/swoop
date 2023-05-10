from __future__ import annotations


from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import (
    AnyUrl,
    BaseModel,
    Extra,
    Field,
    PositiveFloat,
    conint,
    create_model,
)


class Exception(BaseModel):
    class Config:
        extra = Extra.allow

    type: str
    title: str | None = None
    status: int | None = None
    detail: str | None = None
    instance: str | None = None


class ConfClasses(BaseModel):
    conformsTo: list[str]


class Response(Enum):
    raw = "raw"
    document = "document"


class Type(Enum):
    process = "process"


class Link(BaseModel):
    href: str
    rel: str | None = Field(None, example="service")
    type: str | None = Field(None, example="application/json")
    hreflang: str | None = Field(None, example="en")
    title: str | None = None


class MaxOccur(Enum):
    unbounded = "unbounded"


class Subscriber(BaseModel):
    successUri: AnyUrl | None = None
    inProgressUri: AnyUrl | None = None
    failedUri: AnyUrl | None = None


# TODO: How to map these to our statuses?
class StatusCode(Enum):
    accepted = "accepted"
    running = "running"
    successful = "successful"
    failed = "failed"
    dismissed = "dismissed"


# TODO: How we use this is uncertain. We should never execute jobs
# asynchronously, but we may want to return cached results immediately,
# as though the execution had run synchronously.
class JobControlOptions(Enum):
    sync_execute = "sync-execute"
    # async_execute = "async-execute"
    # dismiss = "dismiss"


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


class LandingPage(BaseModel):
    title: str | None = Field(None, example="Example processing server")
    description: str | None = Field(
        None, example="Example server implementing the OGC API - Processes 1.0 Standard"
    )
    links: list[Link]


# TODO: Extend with our state properties as necessary
class StatusInfo(BaseModel):
    processID: str | None = None
    type: Type
    jobID: str
    status: StatusCode
    message: str | None = None
    created: datetime | None = None
    started: datetime | None = None
    finished: datetime | None = None
    updated: datetime | None = None
    progress: conint(ge=0, le=100) | None = None
    links: list[Link] | None = None
    parentID: str | None = None


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


class JobList(BaseModel):
    jobs: list[StatusInfo]
    links: list[Link]


class ProcessSummary(DescriptionType):
    id: str
    version: str
    name: str
    processID: str
    jobControlOptions: list[JobControlOptions] | None = list(JobControlOptions)
    outputTransmission: list[TransmissionMode] | None = None
    description: str | None = None
    handler: str | None = None
    argoTemplate: str | None = None
    cacheEnabled: bool | None = None
    cacheKeyHashIncludes: list[str] | None = None
    cacheKeyHashExcludes: list[str] | None = None
    links: list[Link] | None = None


class QualifiedInputValue(Format):
    value: InputValue


class ProcessList(BaseModel):
    processes: list[ProcessSummary]
    links: list[Link]


class InlineOrRefData(BaseModel):
    __root__: InputValueNoObject | QualifiedInputValue | Link


class Execute(BaseModel):
    # TODO: I believe this is where we need to specify the input payload schema
    inputs: dict[str, InlineOrRefData | list[InlineOrRefData]] | None = None
    # TODO: We should likely omit the ability to specify outputs
    outputs: dict[str, Output] | None = None
    # TODO: Response isn't really to be supported, all results are json
    response: Response | None = "raw"
    subscriber: Subscriber | None = None


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


class InputDescription(DescriptionType):
    minOccurs: int | None = 1
    maxOccurs: int | MaxOccur | None = None
    schema_: Schema = Field(..., alias="schema")


class OutputDescription(DescriptionType):
    schema_: Schema = Field(..., alias="schema")


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


class Process(ProcessSummary):
    inputs: dict[str, InputDescription] | None = None
    outputs: dict[str, OutputDescription] | None = None


Schema.update_forward_refs()


Counts = create_model(
    "Counts",
    **{status.name: (conint(ge=0), ...) for status in StatusCode},
)


class Events(BaseModel):
    pass


class PayloadList(BaseModel):
    pass


class PayloadInfo(BaseModel):
    pass
