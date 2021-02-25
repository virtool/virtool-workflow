import pytest

from virtool_workflow.api.jobs import job_provider
from virtool_workflow.api.scope import api_scope


@pytest.fixture()
async def test_job(connect_to_db):
    dbi = connect_to_db()
    job = {
        "args": {},
        "mem": 8,
        "proc": 3,
        "status": [],
        "task": "test",
    }
    await dbi.jobs.insert_one(job)
    yield job
    await dbi.jobs.delete_one(job)


async def test_job_provider(connect_to_db, test_job):
    _job_provider = await api_scope.instantiate(job_provider)

    job = await _job_provider(job_id=test_job["_id"])

    assert job.key is not None
