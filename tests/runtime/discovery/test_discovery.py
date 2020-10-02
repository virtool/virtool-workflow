from pathlib import Path
from virtool_workflow_runtime import discovery
from virtool_workflow import Workflow

TEST_FILE = Path(__file__).parent/"discoverable_workflow.py"

def test_discover_workflow():
    workflow = discovery.discover_workflow(TEST_FILE)
    assert isinstance(workflow, Workflow)