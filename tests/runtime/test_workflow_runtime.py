from contextlib import suppress

from virtool_workflow import runtime, hooks, data_model
from virtool_workflow.fixtures.errors import FixtureNotAvailable


@hooks.use_job
def make_mock_job():
    return data_model.Job("test_job", {})


async def test_start():
    await runtime.start(dev_mode=True)


async def test_database_accessible():
    @hooks.on_load_database
    def init_db(database):
        init_db.called = True
        assert database
        ...

    @hooks.on_load_fixtures
    def use_db(database):
        use_db.called = True
        assert database

    await runtime.start(direct_db_access_allowed=True)

    assert use_db.called
    assert init_db.called


async def test_database_not_accessible():
    @hooks.on_load_fixtures
    def use_database(database):
        ...

    with suppress(FixtureNotAvailable):
        await runtime.start()
        assert False
