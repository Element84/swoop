from fastapi import FastAPI

from swoop.api.models.workflows import Workflows
from swoop.api.routers.processes import create_workflows_dict


def init_workflows_config(app: FastAPI) -> None:
    """Initialize Workflow Config."""

    wf = Workflows.from_yaml(app.state.settings.workflow_config_file)
    app.state.workflows = create_workflows_dict(wf)
