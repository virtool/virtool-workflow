import asyncio
import os
import shutil
import subprocess

import aioredis
import pytest


@pytest.fixture
def terminated_workflow(tmpdir):
    shutil.copy("tests/files/terminated_workflow.py", "workflow.py")
    yield
    os.remove("workflow.py")


async def test_exit_because_timeout(db, create_job, exec_workflow, job_id, tmpdir):
    """
    Test that the runner exits if no job ID can be pulled from Redis before the timeout.

    This situation does not involve a status update being sent to the server.
    """
    shutil.copy("tests/files/terminated_workflow.py", tmpdir / "workflow.py")

    # This uses the Poetry environment from the calling shell.
    p = subprocess.run(
        [
            "run-workflow",
            "--redis-list-name",
            "jobs_termination",
            "--redis-connection-string",
            "redis://localhost:6379",
            "--timeout",
            "5",
        ],
        capture_output=True,
        encoding="utf-8",
        cwd=tmpdir,
    )

    assert p.returncode == 0
    assert "Waiting for a job" in p.stderr
    assert "Timed out while waiting for job" in p.stderr


async def test_exit_because_sigterm(
    db, create_job, exec_workflow, job_id, jobs_api, tmpdir
):
    shutil.copy("tests/files/terminated_workflow.py", tmpdir / "workflow.py")

    job = await create_job({})

    redis_list_name = f"jobs_{job['workflow']}"

    redis = await aioredis.create_redis_pool("redis://localhost:6379")
    await redis.rpush(redis_list_name, job_id)
    redis.close()
    await redis.wait_closed()

    p = subprocess.Popen(
        [
            "run-workflow",
            "--jobs-api-connection-string",
            jobs_api,
            "--redis-list-name",
            redis_list_name,
            "--redis-connection-string",
            "redis://localhost:6379",
            "--timeout",
            "5",
        ],
        cwd=tmpdir,
    )

    await asyncio.sleep(10)

    p.terminate()
    p.wait()

    assert p.returncode == 124

    document = await db.jobs.find_one()

    assert [(update["state"], update["progress"]) for update in document["status"]] == [
        ("waiting", 0),
        ("preparing", 3),
        ("running", 100),
        ("terminated", 100),
    ]


async def test_exit_because_cancelled(
    db, create_job, exec_workflow, job_id, jobs_api, tmpdir
):
    shutil.copy("tests/files/terminated_workflow.py", tmpdir / "workflow.py")

    job = await create_job({})

    redis_list_name = f"jobs_{job['workflow']}"

    redis = await aioredis.create_redis_pool("redis://localhost:6379")
    await redis.rpush(redis_list_name, job_id)

    p = subprocess.Popen(
        [
            "run-workflow",
            "--jobs-api-connection-string",
            jobs_api,
            "--redis-list-name",
            redis_list_name,
            "--redis-connection-string",
            "redis://localhost:6379",
            "--timeout",
            "5",
        ],
        cwd=tmpdir,
    )

    await asyncio.sleep(5)

    await redis.publish("channel:cancel", job_id)
    redis.close()
    await redis.wait_closed()

    p.wait(timeout=15)

    document = await db.jobs.find_one()

    assert [(update["state"], update["progress"]) for update in document["status"]] == [
        ("waiting", 0),
        ("preparing", 3),
        ("running", 100),
        ("cancelled", 100),
    ]
