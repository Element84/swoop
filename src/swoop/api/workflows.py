from fastapi import FastAPI

from swoop.api.models.workflows import Workflows


def init_workflows_config(app: FastAPI) -> None:
    """Initialize Workflow Config."""

    app.state.workflows = Workflows.from_yaml(app.state.settings.workflow_config_file)
