from virtool_workflow.execution import run_in_executor


async def test_sh():
    out, _ = await run_in_executor.run_shell_command(["ls"])
    assert out
