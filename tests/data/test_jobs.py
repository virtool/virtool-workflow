from pyfixtures import FixtureScope
from syrupy import SnapshotAssertion
from virtool_core.models.job import Job

from tests.fixtures.data import Data


async def test_ok(data: Data, scope: FixtureScope, snapshot: SnapshotAssertion):
    data.job.acquired = False

    job: Job = await scope.get_or_instantiate("job")

    assert job.dict() == snapshot(name="pydantic")
