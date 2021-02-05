from pathlib import Path

from virtool_workflow import runtime, hooks, data_model

WORKFLOW_FILE = Path(__file__).parent / "workflow.py"


@hooks.use_job
def make_mock_job():
    return data_model.Job("test_job", {})


async def test_start():
    await runtime.start(dev_mode=True, workflow_file_path=WORKFLOW_FILE)
