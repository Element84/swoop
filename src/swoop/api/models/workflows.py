from __future__ import annotations

from abc import ABC
from enum import Enum
from pathlib import Path
from typing import Annotated, Literal, Union

import yaml
from pydantic import BaseModel, Field, PrivateAttr, StrictBool, StrictInt, StrictStr

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
    handler: StrictStr
    type: StrictStr

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

    def to_process_summary(self) -> ProcessSummary:
        return ProcessSummary(
            jobControlOptions=[JobControlOptions("async-execute")],
            **self.dict(),
        )

    def to_process(self) -> Process:
        return Process(
            jobControlOptions=[JobControlOptions("async-execute")],
            **self.dict(),
        )


class ArgoWorkflow(BaseWorkflow):
    argoTemplate: StrictStr
    type: Literal["argo-workflow"]


class CirrusWorkflow(BaseWorkflow):
    sfnArn: StrictStr
    type: Literal["cirrus-workflow"]


Workflow = Annotated[
    Union[
        ArgoWorkflow,
        CirrusWorkflow,
    ],
    Field(discriminator="type"),
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
            return cls(cls._type.parse_obj(workflows).__root__)
        except Exception as e:
            raise WorkflowConfigError("Could not load workflow configuration") from e


class Feature(BaseModel):
    id: StrictStr
    collection: StrictStr


class UploadOptions(BaseModel):
    path_template: StrictStr
    collections: dict
    public_assets: list[StrictStr] = []
    headers: dict
    s3_urls: StrictBool


class ProcessDefinition(BaseModel):
    description: StrictStr | None = None
    tasks: dict
    # input_collections: Optional[list[StrictStr]] = None
    upload_options: UploadOptions
    workflow: StrictStr


class Payload(BaseModel):
    type: StrictStr = "FeatureCollection"
    features: list[Feature]
    process: list[ProcessDefinition]


class InputPayload(BaseModel):
    payload: Payload


class Execute(BaseModel):
    # TODO: I believe this is where we need to specify the input payload schema
    # inputs: dict[str, InlineOrRefData | list[InlineOrRefData]] | None = None
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
    type: str
    jobControlOptions: list[JobControlOptions] | None = [
        JobControlOptions("async-execute")
    ]
    outputTransmission: list[TransmissionMode] | None = None
    description: str | None = None
    links: list[Link] | None = None


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
