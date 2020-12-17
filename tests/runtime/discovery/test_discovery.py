from pathlib import Path

from virtool_workflow import Workflow, WorkflowFixture
from virtool_workflow.execution import execution
from virtool_workflow_runtime import discovery

cwd = Path(__file__).parent
TEST_FILE = cwd/"discoverable_workflow.py"
STATIC_TEST_FILE = cwd/"static_workflow.py"

FIXTURE_TEST_FILE = cwd/"discoverable_fixtures.py"

IMPORT_TEST_FILE = cwd/"discoverable_workflow/discoverable_workflow_with_imports.py"


def test_discover_workflow():
    workflow = discovery.discover_workflow(TEST_FILE)
    assert isinstance(workflow, Workflow)


def test_discover_fixtures():
    discovery.discover_fixtures(FIXTURE_TEST_FILE)

    for letter in ("a", "b", "c"):
        assert f"fixture_{letter}" in WorkflowFixture.types()


def test_load_fixtures():
    discovery.load_fixtures_from__fixtures__(FIXTURE_TEST_FILE)

    assert "data_path" in WorkflowFixture.types()
    assert "temp_path" in WorkflowFixture.types()
    assert "thread_pool_executor" in WorkflowFixture.types()


async def test_run_discovery():
    wf = discovery.discover_workflow(FIXTURE_TEST_FILE)
    discovery.load_fixtures_from__fixtures__(FIXTURE_TEST_FILE)
    result = await execution.execute(wf)

    assert result["fixture_a"] == "a"
    assert result["fixture_b"] == "ab"
    assert result["fixture_c"] == "c"
    assert result["data_path"]
    assert result["temp_path"]
    assert result["thread_pool_executor"]
    assert result["run_in_executor"]


async def test_import_workflow_with_other_imports():
    workflow = discovery.discover_workflow(IMPORT_TEST_FILE)

    results = {}
    await workflow.steps[0](results)

    assert results["foo"] == "foo"
    assert results["bar"] == "bar"
    assert results["variable"] is None


