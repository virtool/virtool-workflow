from types import SimpleNamespace

from pytest import fixture

from virtool_workflow.api import jobs
from virtool_workflow.data_model import Status
from virtool_workflow.testing.fixtures import install_as_pytest_fixtures


@fixture
def mem():
    return 8


@fixture
def proc():
    return 4


install_as_pytest_fixtures(globals(), jobs.acquire_job)


async def test_job_can_be_acquired(acquire_job):
    test_job = await acquire_job("test_job")
    assert test_job.key is not None
