import sys
from pathlib import Path

from virtool_workflow_runtime import runtime
from virtool_workflow_runtime.db import VirtoolDatabase
from virtool_workflow_runtime.discovery import discover_workflow
from virtool_workflow.fixtures.scope import WorkflowFixtureScope
from virtool_workflow_runtime.config.environment import db_name, db_connection_string
from virtool_workflow import hooks

EXAMPLE_WORKFLOW_PATH = Path(sys.path[0]).joinpath("tests/example_workflow.py")


async def test_updates_sent_to_mongo():
    with WorkflowFixtureScope() as fixtures:
        name = await fixtures.instantiate(db_name)
        conn = await fixtures.instantiate(db_connection_string)

        db = VirtoolDatabase(name, conn)
        await db._db.jobs.insert_one({"_id": "1"})

    workflow = discover_workflow(EXAMPLE_WORKFLOW_PATH)

    await runtime.execute("1", workflow)

    document = await db._db.jobs.find_one({"_id": "1"})

    updates = [status["update"] for status in document["status"]]

    for update in ("Started up", "Step", "Cleaned up"):
        assert update in updates


async def test_results_stored_when_callback_set():

    with WorkflowFixtureScope() as fixtures:
        db: VirtoolDatabase = await fixtures.instantiate(VirtoolDatabase)
        await db["analyses"].insert_one({"_id": "1"})

        callback = db.store_result_callback("1", db["analyses"], await fixtures.get_or_instantiate("temp_path"))

        hooks.on_result(callback, once=True)

        result = {}

        await hooks.on_result.trigger(None, result)

        document = await db["analyses"].find_one({"_id": "1"})

        assert document["results"] == result
        assert document["ready"]








