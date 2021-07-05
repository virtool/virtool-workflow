from pathlib import Path

from virtool_workflow import Workflow, discovery
from virtool_workflow.analysis.runtime import AnalysisWorkflowEnvironment
from virtool_workflow.fixtures.workflow_fixture import workflow_fixtures
from virtool_workflow.config.fixtures import options

cwd = Path(__file__).parent
TEST_FILE = cwd / "discoverable_workflow.py"
STATIC_TEST_FILE = cwd / "static_workflow.py"

FIXTURE_TEST_FILE = cwd / "discoverable_fixtures.py"

IMPORT_TEST_FILE = cwd / "discoverable_workflow/discoverable_workflow_with_imports.py"


def test_discover_workflow():
    workflow = discovery.discover_workflow(TEST_FILE)
    assert isinstance(workflow, Workflow)


def test_discover_fixtures():
    discovery.discover_fixtures(FIXTURE_TEST_FILE)

    assert all(f"fixture_{letter}" in workflow_fixtures for letter in ("a", "b", "c"))


async def test_run_discovery(runtime: AnalysisWorkflowEnvironment):
    wf = discovery.discover_workflow(FIXTURE_TEST_FILE)
    result = await runtime.execute(wf)

    assert result["fixture_a"] == "a"
    assert result["fixture_b"] == "ab"
    assert result["fixture_c"] == "c"
    assert result["work_path"]


async def test_import_workflow_with_other_imports():
    workflow = discovery.discover_workflow(IMPORT_TEST_FILE)

    results = {}
    await workflow.steps[0](results)

    assert results["foo"] == "foo"
    assert results["bar"] == "bar"
    assert results["variable"] is None
