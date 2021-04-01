from virtool_workflow.discovery import discover_workflow
from virtool_workflow.environment import WorkflowEnvironment
from virtool_workflow.features import install_into_environment, _features
from virtool_workflow.runtime.runtime import prepare_environment
from virtool_workflow.workflow import Workflow


async def test_integration_workflow_is_discoverable(project_root):
    workflow = discover_workflow(project_root / "workflow.py")
    assert isinstance(workflow, Workflow)
    _features.clear()


async def test_workflows_get_merged(project_root):
    environment = WorkflowEnvironment()

    workflow = discover_workflow(project_root / "workflow.py")

    await install_into_environment(environment, workflow=workflow)

    for name in ("test_sample_fixture_available", "test_results_available"):
        assert name in [step.__name__ for step in workflow.steps]
