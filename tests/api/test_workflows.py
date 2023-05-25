from pathlib import Path

import pytest

from swoop.api.exceptions import WorkflowConfigError
from swoop.api.models.workflows import Workflows


def test_loading_workflows(settings):
    name = "mirror"
    workflows = Workflows.from_yaml(settings.workflow_config_file)
    assert name in workflows
    assert hasattr(workflows[name], "name")
    assert workflows[name].name == name


def test_loading_workflows_bad_config_file():
    with pytest.raises(WorkflowConfigError):
        Workflows.from_yaml(Path("./tests/api/bad-workflow-config.yml"))
