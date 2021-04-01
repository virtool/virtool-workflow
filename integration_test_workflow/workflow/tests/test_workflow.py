from virtool_workflow.discovery import discover_workflow
from virtool_workflow.workflow import Workflow


async def test_integration_workflow_is_discoverable(project_root):
    workflow = discover_workflow(project_root / "workflow.py")
    assert isinstance(workflow, Workflow)
