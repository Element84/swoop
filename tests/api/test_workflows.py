from pathlib import Path

import pytest

from swoop.api.exceptions import WorkflowConfigError
from swoop.api.models.workflows import Workflows


@pytest.fixture(scope="session")
def api_fixtures_path(pytestconfig) -> Path:
    return pytestconfig.rootpath.joinpath("tests", "api", "fixtures")


@pytest.fixture(scope="session")
def bad_workflow_config(api_fixtures_path) -> Path:
    return api_fixtures_path.joinpath("bad-workflow-config.yml")


def test_loading_workflows(settings):
    name = "mirror"
    workflows = Workflows.from_yaml(settings.workflow_config_file)
    assert name in workflows
    assert hasattr(workflows[name], "id")
    assert workflows[name].id == name


def test_loading_workflows_bad_config_file(bad_workflow_config):
    with pytest.raises(WorkflowConfigError):
        Workflows.from_yaml(bad_workflow_config)
