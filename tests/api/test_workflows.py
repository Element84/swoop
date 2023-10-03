from pathlib import Path

import pytest

from swoop.api.exceptions import WorkflowConfigError
from swoop.api.models.workflows import BaseWorkflow, Workflows


@pytest.fixture(scope="session")
def api_fixtures_path(pytestconfig) -> Path:
    return pytestconfig.rootpath.joinpath("tests", "api", "fixtures")


@pytest.fixture(scope="session")
def bad_workflow_config(api_fixtures_path) -> Path:
    return api_fixtures_path.joinpath("bad-workflow-config.yml")


def test_loading_workflows(settings):
    name = "mirror"
    workflows = Workflows.from_yaml(settings.config_file)
    assert name in workflows
    assert name in workflows.keys()
    assert hasattr(workflows[name], "id")
    assert workflows[name].id == name
    assert len(workflows) == 2

    for name in workflows:
        assert isinstance(name, str)

    for workflow in workflows.values():
        assert isinstance(workflow, BaseWorkflow)

    for name, workflow in workflows.items():
        assert isinstance(name, str)
        assert isinstance(workflow, BaseWorkflow)


def test_loading_workflows_bad_config_file(bad_workflow_config):
    with pytest.raises(WorkflowConfigError):
        Workflows.from_yaml(bad_workflow_config)
