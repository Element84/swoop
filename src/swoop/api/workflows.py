from fastapi import FastAPI
import yaml


def init_workflows_config(app: FastAPI) -> None:
    """Initialize Workflow Config."""
    app.state.workflows = yaml.safe_load(
        open(app.state.settings.swoop_workflow_config_file)
    )
