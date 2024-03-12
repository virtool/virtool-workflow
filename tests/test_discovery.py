from pathlib import Path


from virtool_workflow import Workflow
from virtool_workflow.runtime.discover import discover_workflow


def test_discover_workflow(example_path: Path):
    """Test that a workflow can be discovered from a module."""

    workflow = discover_workflow(Path(__file__).parent.parent / "workflow.py")

    assert isinstance(workflow, Workflow)
    assert len(workflow.steps) == 2
    assert workflow.steps[0].display_name == "Step 1"
    assert workflow.steps[1].display_name == "Try Fastqc"
    assert (
        workflow.steps[0].description
        == "A basic step that doesn't actually do anything."
    )
    assert (
        workflow.steps[1].description
        == "Make sure the FastQC fixture works in a real workflow run."
    )
