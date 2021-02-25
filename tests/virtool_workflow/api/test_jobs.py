import pytest


@pytest.fixture
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


async def test_job_can_be_acquired(connect_to_db, test_job, acquire_job):
    _job_provider = await api_scope.instantiate(job_provider)

    job = await _job_provider(job_id=test_job["_id"])

    assert job.key is not None
