from swoop.api.models.workflows import Workflows


def test_loading_workflows(settings):
    name = "mirror"
    workflows = Workflows.from_yaml(settings.workflow_config_file)
    assert name in workflows
    assert hasattr(workflows[name], "name")
    assert workflows[name].name == name
