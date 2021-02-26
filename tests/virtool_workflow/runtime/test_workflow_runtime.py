from pathlib import Path

from virtool_workflow import runtime

WORKFLOW_FILE = Path(__file__).parent / "workflow.py"


async def test_start(http):
    await runtime.start(dev_mode=True, workflow_file_path=WORKFLOW_FILE, job_api_url="")
