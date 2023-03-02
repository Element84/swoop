from __future__ import annotations

import types

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

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
    title: Optional[str] = None
    status: Optional[int] = None
    detail: Optional[str] = None
    instance: Optional[str] = None


class ConfClasses(BaseModel):
    conformsTo: List[str]


class Response(Enum):
    raw = 'raw'
    document = 'document'


class Type(Enum):
    process = 'process'


class Link(BaseModel):
    href: str
    rel: Optional[str] = Field(None, example='service')
    type: Optional[str] = Field(None, example='application/json')
    hreflang: Optional[str] = Field(None, example='en')
    title: Optional[str] = None


class MaxOccur(Enum):
    unbounded = 'unbounded'


class Subscriber(BaseModel):
    successUri: Optional[AnyUrl] = None
    inProgressUri: Optional[AnyUrl] = None
    failedUri: Optional[AnyUrl] = None


# TODO: How to map these to our statuses?
class StatusCode(Enum):
    accepted = 'accepted'
    running = 'running'
    successful = 'successful'
    failed = 'failed'
    dismissed = 'dismissed'


# TODO: How we use this is uncertain. We should never execute jobs
# asynchronously, but we may want to return cached results immediately,
# as though the execution had run synchronously.
class JobControlOptions(Enum):
    sync_execute = 'sync-execute'
    async_execute = 'async-execute'
    dismiss = 'dismiss'


class TransmissionMode(Enum):
    value = 'value'
    reference = 'reference'


class Type1(Enum):
    array = 'array'
    boolean = 'boolean'
    integer = 'integer'
    number = 'number'
    object = 'object'
    string = 'string'


class Format(BaseModel):
    mediaType: Optional[str] = None
    encoding: Optional[str] = None
    schema_: Optional[Union[str, Dict[str, Any]]] = Field(None, alias='schema')


class Metadata(BaseModel):
    title: Optional[str] = None
    role: Optional[str] = None
    href: Optional[str] = None


class AdditionalParameter(BaseModel):
    name: str
    value: List[Union[str, float, int, List[Dict[str, Any]], Dict[str, Any]]]


class Reference(BaseModel):
    field_ref: str = Field(..., alias='$ref')


class BinaryInputValue(BaseModel):
    __root__: str


class Crs(Enum):
    http___www_opengis_net_def_crs_OGC_1_3_CRS84 = (
        'http://www.opengis.net/def/crs/OGC/1.3/CRS84'
    )
    http___www_opengis_net_def_crs_OGC_0_CRS84h = (
        'http://www.opengis.net/def/crs/OGC/0/CRS84h'
    )


class Bbox(BaseModel):
    bbox: List[float]
    crs: Optional[Crs] = 'http://www.opengis.net/def/crs/OGC/1.3/CRS84'


class LandingPage(BaseModel):
    title: Optional[str] = Field(None, example='Example processing server')
    description: Optional[str] = Field(
        None, example='Example server implementing the OGC API - Processes 1.0 Standard'
    )
    links: List[Link]


# TODO: Extend with our state properties as necessary
class StatusInfo(BaseModel):
    processID: Optional[str] = None
    type: Type
    jobID: str
    status: StatusCode
    message: Optional[str] = None
    created: Optional[datetime] = None
    started: Optional[datetime] = None
    finished: Optional[datetime] = None
    updated: Optional[datetime] = None
    progress: Optional[conint(ge=0, le=100)] = None
    links: Optional[List[Link]] = None
    parentID: Optional[str] = None


class Output(BaseModel):
    format: Optional[Format] = None
    transmissionMode: Optional[TransmissionMode] = 'value'


class AdditionalParameters(Metadata):
    parameters: Optional[List[AdditionalParameter]] = None


class DescriptionType(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    keywords: Optional[List[str]] = None
    metadata: Optional[List[Metadata]] = None
    additionalParameters: Optional[AdditionalParameters] = None


class InputValueNoObject(BaseModel):
    __root__: Union[str, float, int, bool, List[str], BinaryInputValue, Bbox]


class InputValue(BaseModel):
    __root__: Union[InputValueNoObject, Dict[str, Any]]


class JobList(BaseModel):
    jobs: List[StatusInfo]
    links: List[Link]


class ProcessSummary(DescriptionType):
    id: str
    version: str
    jobControlOptions: Optional[List[JobControlOptions]] = None
    outputTransmission: Optional[List[TransmissionMode]] = None
    links: Optional[List[Link]] = None


class QualifiedInputValue(Format):
    value: InputValue


class ProcessList(BaseModel):
    processes: List[ProcessSummary]
    links: List[Link]


class InlineOrRefData(BaseModel):
    __root__: Union[InputValueNoObject, QualifiedInputValue, Link]


class Execute(BaseModel):
    # TODO: I believe this is where we need to specify the input payload schema
    inputs: Optional[dict[str, Union[InlineOrRefData, list[InlineOrRefData]]]] = None
    # TODO: We should likely omit the ability to specify outputs
    outputs: Optional[dict[str, Output]] = None
    # TODO: Response isn't really to be supported, all results are json
    response: Optional[Response] = 'raw'
    subscriber: Optional[Subscriber] = None

class Results(BaseModel):
    # TODO: This becomes the schema of the workflow output
    __root__: Optional[dict[str, InlineOrRefData]] = None


class InlineResponse200(BaseModel):
    __root__: Union[
        str, float, int, dict[str, Any], list[dict[str, Any]], bool, bytes, Results
    ]


class Schema(BaseModel):
    __root__: Union[Reference, SchemaItem]


class InputDescription(DescriptionType):
    minOccurs: Optional[int] = 1
    maxOccurs: Optional[Union[int, MaxOccur]] = None
    schema_: Schema = Field(..., alias='schema')


class OutputDescription(DescriptionType):
    schema_: Schema = Field(..., alias='schema')


class SchemaItem(BaseModel):
    class Config:
        extra = Extra.forbid

    title: Optional[str] = None
    multipleOf: Optional[PositiveFloat] = None
    maximum: Optional[float] = None
    exclusiveMaximum: Optional[bool] = False
    minimum: Optional[float] = None
    exclusiveMinimum: Optional[bool] = False
    maxLength: Optional[conint(ge=0)] = None
    minLength: Optional[conint(ge=0)] = 0
    pattern: Optional[str] = None
    maxItems: Optional[conint(ge=0)] = None
    minItems: Optional[conint(ge=0)] = 0
    uniqueItems: Optional[bool] = False
    maxProperties: Optional[conint(ge=0)] = None
    minProperties: Optional[conint(ge=0)] = 0
    required: Optional[List[str]] = Field(None, min_items=1, unique_items=True)
    enum: Optional[List[Dict[str, Any]]] = Field(None, min_items=1, unique_items=False)
    type: Optional[Type1] = None
    not_: Optional[Union[Schema, Reference]] = Field(None, alias='not')
    allOf: Optional[List[Union[Schema, Reference]]] = None
    oneOf: Optional[List[Union[Schema, Reference]]] = None
    anyOf: Optional[List[Union[Schema, Reference]]] = None
    items: Optional[Union[Schema, Reference]] = None
    properties: Optional[Dict[str, Union[Schema, Reference]]] = None
    additionalProperties: Optional[Union[Schema, Reference, bool]] = True
    description: Optional[str] = None
    format: Optional[str] = None
    default: Optional[Dict[str, Any]] = None
    nullable: Optional[bool] = False
    readOnly: Optional[bool] = False
    writeOnly: Optional[bool] = False
    example: Optional[Dict[str, Any]] = None
    deprecated: Optional[bool] = False
    contentMediaType: Optional[str] = None
    contentEncoding: Optional[str] = None
    contentSchema: Optional[str] = None


class Process(ProcessSummary):
    inputs: Optional[dict[str, InputDescription]] = None
    outputs: Optional[dict[str, OutputDescription]] = None


Schema.update_forward_refs()


Counts = create_model(
    'Counts',
    **{status.name: (conint(ge=0), ...) for status in StatusCode},
)


class Events(BaseModel):
    pass


class PayloadList(BaseModel):
    pass


class PayloadInfo(BaseModel):
    pass
