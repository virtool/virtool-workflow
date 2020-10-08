from virtool_workflow import execute


async def test_sh():
    out, _ = await execute.run_shell_command("ls")
    assert out
