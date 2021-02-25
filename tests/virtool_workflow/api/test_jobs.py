import pytest

from virtool_workflow.api.scope import api_fixtures
from virtool_workflow.testing import install_as_pytest_fixtures

install_as_pytest_fixtures(globals(), *api_fixtures.values())


@pytest.mark.asyncio
async def test_job_can_be_acquired(test_job, acquire_job):
    job = await acquire_job(test_job["_id"])
    assert job.key is not None
