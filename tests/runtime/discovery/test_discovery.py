from pathlib import Path
from virtool_workflow_runtime import discovery
from virtool_workflow import Workflow

cwd = Path(__file__).parent
TEST_FILE = cwd/"discoverable_workflow.py"
STATIC_TEST_FILE = cwd/"static_workflow.py"


def test_discover_workflow():
    workflow = discovery.discover_workflow(TEST_FILE)
    assert isinstance(workflow, Workflow)


