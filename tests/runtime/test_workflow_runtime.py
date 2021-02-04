from contextlib import suppress

from pathlib import Path

from virtool_workflow import runtime, hooks, data_model
from virtool_workflow.db.mongo import VirtoolMongoDB
from virtool_workflow.fixtures.errors import FixtureNotAvailable

WORKFLOW_FILE = Path(__file__).parent / "workflow.py"


@hooks.use_job
def make_mock_job():
    return data_model.Job("test_job", {})


async def test_start():
    await runtime.start(dev_mode=True, workflow_file_path=WORKFLOW_FILE)


async def test_database_not_accessible():
    @hooks.on_load_fixtures
    def use_database(database):
        ...

    with suppress(FixtureNotAvailable):
        await runtime.start()
        assert False


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

    await runtime.start(direct_db_access_allowed=True, workflow_file_path=WORKFLOW_FILE)

    assert use_db.called
    assert init_db.called


async def test_use_mongo_database():
    @hooks.on_load_database
    def use_mongo(database):
        use_mongo.called = True
        assert isinstance(database, VirtoolMongoDB)

    await runtime.start(db_type="mongo", workflow_file_path=WORKFLOW_FILE)

    assert use_mongo.called
