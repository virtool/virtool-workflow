import asyncio

import pytest

from virtool_workflow import hooks
from virtool_workflow.runtime.run_subprocess import run_subprocess as _run_subprocess
from virtool_workflow.runtime.run_subprocess import SubprocessFailed

run_subprocess = _run_subprocess()


@pytest.fixture
def bash(tmpdir):
    sh = """
    echo "hello world"
    echo "foo bar"
    """

    path = tmpdir / "test.sh"
    path.write(sh)

    return path


@pytest.fixture
def bash_sleep(tmpdir):
    txt_path = tmpdir / "test.txt"

    sh = f"""
    sleep 100
    touch {txt_path}
    """

    sh_path = tmpdir / "test.sh"
    sh_path.write(sh)

    return sh_path, txt_path


async def test_command_is_called(tmpdir):
    path = tmpdir / "test.txt"
    assert not path.isfile()

    await run_subprocess(["touch", str(path)])

    assert path.isfile()


async def test_stdout_is_handled(bash):
    lines = list()

    async def stdout_handler(line):
        lines.append(line)

    await run_subprocess(["bash", str(bash)], stdout_handler=stdout_handler)

    assert lines == [b"hello world\n", b"foo bar\n"]


async def test_stderr_is_handled(bash):
    lines = list()

    async def stderr_handler(line):
        lines.append(line)

    with pytest.raises(SubprocessFailed):
        await run_subprocess(["bash", "/foo/bar"], stderr_handler=stderr_handler)

    assert lines == [b"bash: /foo/bar: No such file or directory\n"]


async def trigger_finish(test_workflow, scope):
    try:
        await asyncio.sleep(1)
        raise Exception("Foo")
    except Exception as error:
        scope["error"] = error
        await hooks.on_failure.trigger(scope)


async def test_command_can_be_terminated(bash_sleep, test_workflow, runtime):
    sh_path, txt_path = bash_sleep

    t1 = asyncio.create_task(trigger_finish(test_workflow, runtime))
    t2 = asyncio.create_task(run_subprocess(["bash", str(sh_path)]))

    await asyncio.gather(t1, t2)

    assert not txt_path.isfile()


async def test_run_subprocess_does_raise_subprocess_failed():
    with pytest.raises(SubprocessFailed):
        await run_subprocess(["ls", "-doesnotexist"])

    await run_subprocess(["ls"])
