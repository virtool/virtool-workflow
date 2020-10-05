from pathlib import Path
from virtool_workflow_runtime import discovery
from virtool_workflow import Workflow, decorator_api

cwd = Path(__file__).parent
TEST_FILE = cwd/"discoverable_workflow.py"
STATIC_TEST_FILE = cwd/"static_workflow.py"


def test_discover_workflow():
    workflow = discovery.discover_workflow(TEST_FILE)
    assert isinstance(workflow, Workflow)


async def test_discover_static_workflow():
    wf = discovery.discover_workflow(STATIC_TEST_FILE)
    assert wf == decorator_api.workflow
    assert len(wf.steps) > 0 and len(wf.on_startup) > 0 and len(wf.on_cleanup) > 0
    result = await decorator_api.execute_workflow()
    assert decorator_api.workflow.results == result
    assert result["start"] and result["clean"] and result["step"]
