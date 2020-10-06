from virtool_workflow import run


def test_sh():
    out, _ = run.sh("ls -la")
    assert out
