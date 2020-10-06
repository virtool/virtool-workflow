from virtool_workflow import execute


async def test_sh():
    out, _ = await execute.shell("ls")
    assert out
