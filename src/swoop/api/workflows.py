import yaml
from fastapi import FastAPI


def init_workflows_config(app: FastAPI) -> None:
    """Initialize Workflow Config."""
    app.state.workflows = yaml.safe_load(open(app.state.settings.workflow_config_file))
