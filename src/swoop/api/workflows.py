from fastapi import FastAPI
import yaml


def init_workflows_config(app: FastAPI) -> None:
    """Initialize Workflow Config."""
    app.state.workflows = yaml.full_load(open(app.state.settings.workflow_config_file))
