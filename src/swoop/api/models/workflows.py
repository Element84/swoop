from __future__ import annotations

from abc import ABC
from enum import Enum
from pathlib import Path
from typing import Annotated, Literal, Union

import yaml
from fastapi import Request
from pydantic import (
    UUID5,
    BaseModel,
    BeforeValidator,
    Field,
    PrivateAttr,
    RootModel,
    StrictInt,
    StrictStr,
    conint,
    conlist,
    field_validator,
)

from swoop.api.exceptions import WorkflowConfigError
from swoop.api.models.shared import DescriptionType, Link, Schema, TransmissionMode
from swoop.cache.types import JSONFilter
from swoop.cache.uuid import generate_payload_uuid


class Response(Enum):
    # raw = "raw"
    document = "document"


class Handler(BaseModel, extra="allow"):
    id: StrictStr
    type: StrictStr


class BaseWorkflow(BaseModel, ABC, extra="allow"):
    id: StrictStr
    title: str = ""
    description: StrictStr
    version: StrictInt
    cacheKeyHashIncludes: list[StrictStr] = []
    cacheKeyHashExcludes: list[StrictStr] = []
    _json_filter: JSONFilter = PrivateAttr()
    handler: StrictStr
    handlerType: StrictStr
    links: list[Link] = []

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        if not self.title:
            self.title = self.id
        self._json_filter: JSONFilter = JSONFilter(
            self.cacheKeyHashIncludes,
            self.cacheKeyHashExcludes,
        )

    def generate_payload_uuid(self, payload: Payload) -> UUID5:
        return generate_payload_uuid(self.id, self._json_filter(payload.model_dump()))

    def to_process_summary(self, request: Request | None = None) -> ProcessSummary:
        return ProcessSummary(
            jobControlOptions=[JobControlOptions("async-execute")],
            request=request,
            **self.__dict__,
        )

    def to_process(self, request: Request | None = None) -> Process:
        return Process(
            jobControlOptions=[JobControlOptions("async-execute")],
            request=request,
            **self.__dict__,
        )


class ArgoWorkflow(BaseWorkflow):
    argoTemplate: StrictStr
    handlerType: Literal["argoWorkflow"]


class CirrusWorkflow(BaseWorkflow):
    sfnArn: StrictStr
    handlerType: Literal["cirrusWorkflow"]


Workflow = Annotated[
    Union[
        ArgoWorkflow,
        CirrusWorkflow,
    ],
    Field(discriminator="handlerType"),
]


class Workflows(RootModel[dict[str, Workflow]]):
    @classmethod
    def from_yaml(cls, path: Path) -> Workflows:
        try:
            loaded = yaml.safe_load(path.read_text())

            handlers = {}
            for name, handler in loaded["handlers"].items():
                handler["id"] = name
                handlers[name] = Handler(**handler)

            workflows = dict(sorted(loaded["workflows"].items()))
            for name, workflow in workflows.items():
                workflow["id"] = name
                workflow["handlerType"] = handlers[workflow["handler"]].type

            return cls(**workflows)
        except Exception as e:
            raise WorkflowConfigError("Could not load workflow configuration") from e

    def __getitem__(self, key) -> Workflow:
        return self.root[key]

    def __len__(self) -> int:
        return len(self.root)

    def __iter__(self):
        yield from self.root

    def __contains__(self, key):
        return key in self.root

    def keys(self):
        return self.root.keys()

    def values(self):
        return self.root.values()

    def items(self):
        return self.root.items()


class Feature(BaseModel, extra="allow"):
    id: StrictStr
    collection: StrictStr | None = None


class UploadOptions(BaseModel, extra="allow"):
    path_template: StrictStr
    collections: dict

    @field_validator("collections")
    def collections_must_contain_at_least_one_item(cls, v):
        if not v:
            raise ValueError("Collections must contain at least one item in the map")
        return v


class ProcessDefinition(BaseModel, extra="allow"):
    description: StrictStr | None = None
    tasks: dict = {}
    upload_options: UploadOptions
    workflow: StrictStr


ProcessArray = conlist(ProcessDefinition | list[ProcessDefinition], min_length=1)


class Payload(BaseModel):
    type: StrictStr = "FeatureCollection"
    features: list[Feature] = []
    process: ProcessArray

    @field_validator("process")
    def first_item_cannot_be_list(cls, v):
        if not isinstance(v[0], ProcessDefinition):
            raise ValueError("first element in the `process` array cannot be an array")
        return v

    def current_process_definition(self) -> ProcessDefinition:
        if not isinstance(self.process[0], ProcessDefinition):
            raise ValueError("first element in the `process` array cannot be an array")
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
    version: Annotated[str, BeforeValidator(lambda x: str(x))]
    handlerType: str
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
                        request.url_for("get_workflow_description", processID=self.id)
                    ),
                ),
            ]


class MaxOccur(Enum):
    unbounded = "unbounded"


class InputDescription(DescriptionType):
    minOccurs: conint(ge=0) = 1
    maxOccurs: conint(ge=0) | MaxOccur = "unbounded"
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
