from virtool_workflow_runtime import runtime
from virtool_workflow_runtime.db import VirtoolDatabase
from virtool_workflow_runtime.config.configuration import db_name, db_connection_string


async def test_execute(test_workflow, empty_scope):
    db = VirtoolDatabase(db_name(), db_connection_string())

    await db["jobs"].insert_one(dict(_id="1", args=dict()))

    await runtime.execute("1", test_workflow, empty_scope)
