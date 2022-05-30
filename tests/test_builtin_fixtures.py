from pyfixtures import runs_in_new_fixture_context, FixtureScope
from virtool_workflow.builtin_fixtures import work_path
from pathlib import Path


@runs_in_new_fixture_context(work_path, copy_context=False)
async def test_work_path():
    async with FixtureScope() as scope:
        scope["config"] = {"work_path": "temp"}
        path = await scope.instantiate_by_key("work_path")

        assert isinstance(path, Path)
        assert path.exists

    assert not path.exists()
