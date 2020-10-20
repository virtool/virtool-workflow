from pathlib import Path
from virtool_workflow_runtime import discovery
from virtool_workflow import Workflow, WorkflowFixture

cwd = Path(__file__).parent
TEST_FILE = cwd/"discoverable_workflow.py"
STATIC_TEST_FILE = cwd/"static_workflow.py"

FIXTURE_TEST_FILE = cwd/"discoverable_fixtures.py"


def test_discover_workflow():
    workflow = discovery.discover_workflow(TEST_FILE)
    assert isinstance(workflow, Workflow)


def test_discover_fixtures():
    discovery.discover_fixtures(FIXTURE_TEST_FILE)

    for letter in ("a", "b", "c"):
        assert f"fixture_{letter}" in WorkflowFixture.types()


