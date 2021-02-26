from pathlib import Path

from virtool_workflow import runtime
from virtool_workflow.api.scope import api_fixtures

WORKFLOW_FILE = Path(__file__).parent / "workflow.py"


async def test_start(http, jobs_api_url):
    api_fixtures["http"] = lambda: http
    await runtime.start(dev_mode=True, workflow_file_path=WORKFLOW_FILE, jobs_api_url="/api")
