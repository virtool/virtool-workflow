from pathlib import Path
from virtool_workflow_runtime import runtime, db
from virtool_workflow_runtime.discovery import discover_workflow


async def test_updates_sent_to_mongo():
    workflow = discover_workflow(Path("example_workflow.py"))
    result = await runtime.execute(workflow, "1", database_name="test")
