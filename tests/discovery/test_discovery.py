from pathlib import Path

from pyfixtures import get_fixtures
from virtool_workflow import Workflow, discovery

cwd = Path(__file__).parent
TEST_FILE = cwd / "discoverable_workflow.py"
STATIC_TEST_FILE = cwd / "static_workflow.py"

FIXTURE_TEST_FILE = cwd / "discoverable_fixtures.py"

IMPORT_TEST_FILE = cwd / "discoverable_workflow_with_imports/__main__.py"


def test_discover_workflow():
    workflow = discovery.discover_workflow(TEST_FILE)
    assert isinstance(workflow, Workflow)


def test_discover_fixtures():
    discovery.discover_fixtures(FIXTURE_TEST_FILE)

    fixtures = get_fixtures()

    assert all(f"fixture_{letter}" in fixtures for letter in ("a", "b", "c"))


async def test_run_discovery(runtime):
    wf = discovery.discover_workflow(FIXTURE_TEST_FILE)
    result = await runtime.execute(wf)

    assert result["fixture_a"] == "a"
    assert result["fixture_b"] == "ab"
    assert result["fixture_c"] == "c"


async def test_import_workflow_with_other_imports():
    workflow = discovery.discover_workflow(IMPORT_TEST_FILE)

    results = {}
    await workflow.steps[0](results)

    assert results["foo"] == "foo"
    assert results["bar"] == "bar"
