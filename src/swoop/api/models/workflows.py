from __future__ import annotations

from abc import ABC
from enum import Enum
from pathlib import Path
from typing import Annotated, Literal, Union

import yaml
from fastapi import Request
from pydantic import (
    BaseModel,
    Extra,
    Field,
    PrivateAttr,
    StrictInt,
    StrictStr,
    conlist,
    validator,
)

from swoop.api.exceptions import WorkflowConfigError
from swoop.api.models.shared import DescriptionType, Link, Schema, TransmissionMode
from swoop.cache.hashing import hash_dict
from swoop.cache.types import JSONFilter


class Response(Enum):
    # raw = "raw"
    document = "document"


class BaseWorkflow(BaseModel, ABC):
    id: StrictStr
    title: str = ""
    description: StrictStr
    version: StrictInt
    cacheKeyHashIncludes: list[StrictStr] = []
    cacheKeyHashExcludes: list[StrictStr] = []
    _json_filter: JSONFilter = PrivateAttr()
    handler_name: StrictStr
    handler_type: StrictStr
    links: list[Link] = []

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        if not self.title:
            self.title = self.id
        self._json_filter: JSONFilter = JSONFilter(
            self.cacheKeyHashIncludes,
            self.cacheKeyHashExcludes,
        )

    def hash_payload(self, payload) -> bytes:
        return hash_dict(self._json_filter(payload))

    def to_process_summary(self, request: Request | None = None) -> ProcessSummary:
        return ProcessSummary(
            jobControlOptions=[JobControlOptions("async-execute")],
            request=request,
            **self.dict(),
        )

    def to_process(self, request: Request | None = None) -> Process:
        return Process(
            jobControlOptions=[JobControlOptions("async-execute")],
            request=request,
            **self.dict(),
        )


class ArgoWorkflow(BaseWorkflow):
    argoTemplate: StrictStr
    handler_type: Literal["argo-workflow"]


class CirrusWorkflow(BaseWorkflow):
    sfnArn: StrictStr
    handler_type: Literal["cirrus-workflow"]


Workflow = Annotated[
    Union[
        ArgoWorkflow,
        CirrusWorkflow,
    ],
    Field(discriminator="handler_type"),
]


class Workflows(dict[str, Workflow]):
    class _type(BaseModel):
        __root__: dict[str, Workflow]

    @classmethod
    def from_yaml(cls, path: Path) -> Workflows:
        try:
            workflows = yaml.safe_load(path.read_text())["workflows"]
            for name, workflow in workflows.items():
                workflow["id"] = name
            return cls(**cls._type.parse_obj(workflows).__root__)
        except Exception as e:
            raise WorkflowConfigError("Could not load workflow configuration") from e


class Feature(BaseModel, extra=Extra.allow):
    id: StrictStr
    collection: StrictStr | None = None


class UploadOptions(BaseModel, extra=Extra.allow):
    path_template: StrictStr
    collections: dict

    @validator("collections")
    def collections_must_contain_at_least_one_item(cls, v):
        if not v:
            raise ValueError("Collections must contain at least one item in the map")
        return v


class ProcessDefinition(BaseModel, extra=Extra.allow):
    description: StrictStr | None = None
    tasks: dict = {}
    upload_options: UploadOptions
    workflow: StrictStr


class Payload(BaseModel, smart_union=True):
    type: StrictStr = "FeatureCollection"
    features: list[Feature] = []
    process: conlist(ProcessDefinition | list[ProcessDefinition], min_items=1)

    @validator("process")
    def first_item_cannot_be_list(cls, v):
        if not isinstance(v[0], ProcessDefinition):
            raise ValueError("first element in the `process` array cannot be an array")
        return v

    def current_process_definition(self) -> ProcessDefinition:
        return self.process[0]


class InputPayload(BaseModel):
    payload: Payload


class Execute(BaseModel):
    inputs: InputPayload
    # TODO: We should likely omit the ability to specify outputs
    # outputs: dict[str, Output] | None = None
    # TODO: Response isn't really to be supported, all results are json
    response: Literal["document"] = "document"
    # subscriber: Subscriber | None = None


# TODO: How we use this is uncertain. We should never execute jobs
# asynchronously, but we may want to return cached results immediately,
# as though the execution had run synchronously.
class JobControlOptions(Enum):
    # sync_execute = "sync-execute"
    async_execute = "async-execute"
    # dismiss = "dismiss"


class ProcessSummary(DescriptionType):
    id: str
    version: str
    handler_type: str
    jobControlOptions: list[JobControlOptions] | None = [
        JobControlOptions("async-execute")
    ]
    outputTransmission: list[TransmissionMode] | None = None
    description: str | None = None
    links: list[Link] = []

    def __init__(self, request: Request | None = None, **kwargs):
        super().__init__(**kwargs)

        if request:
            self.links += [
                Link.root_link(request),
                Link.self_link(
                    href=str(
                        request.url_for("get_process_description", processID=self.id)
                    ),
                ),
            ]


class MaxOccur(Enum):
    unbounded = "unbounded"


class InputDescription(DescriptionType):
    minOccurs: int | None = 1
    maxOccurs: int | MaxOccur | None = None
    schema_: Schema = Field(..., alias="schema")


class OutputDescription(DescriptionType):
    schema_: Schema = Field(..., alias="schema")


class Process(ProcessSummary):
    inputs: dict[str, InputDescription] | None = None
    outputs: dict[str, OutputDescription] | None = None
    cacheKeyHashIncludes: list[str] | None = None
    cacheKeyHashExcludes: list[str] | None = None


class ProcessList(BaseModel):
    processes: list[ProcessSummary]
    links: list[Link]
