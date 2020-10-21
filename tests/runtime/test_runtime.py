from virtool_workflow_runtime import runtime


async def test_execute(test_workflow):
    await runtime.execute("1", test_workflow)
