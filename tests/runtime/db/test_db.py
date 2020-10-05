from pathlib import Path
from virtool_workflow_runtime import runtime
from virtool_workflow_runtime.db import database
from virtool_workflow_runtime.discovery import discover_workflow


async def test_updates_sent_to_mongo():
    db = database("test")
    await db.jobs.insert_one({"_id": "1"})

    workflow = discover_workflow(Path("example_workflow.py"))
    await runtime.execute(workflow, "1", database_name="test")

    document = await database("test").jobs.find_one({"_id": "1"})

    updates = [status["update"] for status in document["status"]]

    for update in ("Started up", "Step", "Cleaned up"):
        assert update in updates
