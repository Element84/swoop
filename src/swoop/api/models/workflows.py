from __future__ import annotations

from enum import Enum
from pathlib import Path

import yaml
from pydantic import BaseModel, StrictBool, StrictInt, StrictStr


class Response(Enum):
    # raw = "raw"
    document = "document"


class Workflow(BaseModel):
    name: StrictStr
    description: StrictStr
    version: StrictInt
    handler: StrictStr | None = None
    cacheKeyHashIncludes: list[StrictStr] | None = None
    cacheKeyHashExcludes: list[StrictStr] | None = None


class ArgoWorkflow(Workflow):
    workflow_template: StrictStr


class CirrusWorkflow(Workflow):
    sfn_arn: StrictStr


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
    response: Response | None = "document"
    # subscriber: Subscriber | None = None


class Workflows(dict):
    @classmethod
    def from_yaml(cls, path: Path) -> dict:
        with open(path) as f:
            workflows = yaml.safe_load(f)
            return workflows
