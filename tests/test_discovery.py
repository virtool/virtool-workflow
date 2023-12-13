from pathlib import Path


from virtool_workflow import Workflow
from virtool_workflow.runtime.discover import discover_workflow


def test_discover_workflow(example_path: Path):
    """Test that a workflow can be discovered from a module."""

    workflow = discover_workflow(example_path / "modules" / "_workflow.py")

    assert isinstance(workflow, Workflow)
    assert len(workflow.steps) == 2
    assert workflow.steps[0].display_name == "Step One"
    assert workflow.steps[1].display_name == "Step 2"
    assert workflow.steps[0].description == "This is a description for the first step."
    assert workflow.steps[1].description == "This is a description for the second step."
