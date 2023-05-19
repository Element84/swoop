from __future__ import annotations

from abc import ABC
from enum import Enum
from pathlib import Path
from typing import Annotated, Literal, Union

import yaml
from pydantic import BaseModel, Field, StrictBool, StrictInt, StrictStr

from swoop.api.exceptions import WorkflowConfigError


class Response(Enum):
    # raw = "raw"
    document = "document"


class BaseWorkflow(BaseModel, ABC):
    name: StrictStr
    description: StrictStr
    version: StrictInt
    cache_key_hash_includes: list[StrictStr] = []
    cache_key_hash_excludes: list[StrictStr] = []


class ArgoWorkflow(BaseWorkflow):
    handler: Literal["argo-workflow"]
    argo_template: StrictStr


class CirrusWorkflow(BaseWorkflow):
    handler: Literal["cirrus-workflow"]
    sfn_arn: StrictStr


Workflow = Annotated[
    Union[
        ArgoWorkflow,
        CirrusWorkflow,
    ],
    Field(discriminator="handler"),
]


class Feature(BaseModel):
    id: StrictStr
    collection: StrictStr


class UploadOptions(BaseModel):
    path_template: StrictStr
    collections: dict
    public_assets: list[StrictStr] = []
    headers: dict
    s3_urls: StrictBool


class Process(BaseModel):
    description: StrictStr | None = None
    tasks: dict
    # input_collections: Optional[list[StrictStr]] = None
    upload_options: UploadOptions


class Payload(BaseModel):
    id: StrictStr
    type: StrictStr = "FeatureCollection"
    features: list[Feature]
    process: list[Process] | Process


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


class Workflows(dict[str, Workflow]):
    class _type(BaseModel):
        __root__: dict[str, Workflow]

    @classmethod
    def from_yaml(cls, path: Path) -> Workflows:
        try:
            workflows = yaml.safe_load(path.read_text())["workflows"]
            for name, workflow in workflows.items():
                workflow["name"] = name
            return cls(cls._type.parse_obj(workflows).__root__)
        except Exception as e:
            raise WorkflowConfigError("Could not load workflow configuration") from e
