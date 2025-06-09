from pyfixtures import FixtureScope
from syrupy import SnapshotAssertion
from virtool.jobs.models import Job

from virtool_workflow.pytest_plugin.data import Data


async def test_ok(data: Data, scope: FixtureScope, snapshot: SnapshotAssertion):
    data.job.acquired = False

    job: Job = await scope.get_or_instantiate("job")

    assert job.dict() == snapshot(name="pydantic")
