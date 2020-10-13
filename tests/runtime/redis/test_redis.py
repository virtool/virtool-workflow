import pytest
import aioredis
import asyncio

import motor.motor_asyncio
from virtool_workflow_runtime.db import VirtoolDatabase, DATABASE_CONNECTION_URL_DEFAULT
from virtool_workflow_runtime._redis import job_id_queue, connect, VIRTOOL_JOBS_CHANNEL




@pytest.fixture
def redis_url():
    return "redis://localhost:6379/1"


async def assert_correct_job_ids(redis_url):
    queue = job_id_queue(redis_url)
    _1 = await queue.__anext__()
    assert _1.decode("utf-8") == "1"


async def publish_job_ids(redis_url):
    async with connect(redis_url) as redis:
        for id_ in ["1", "2", "3"]:
            redis.publish(VIRTOOL_JOBS_CHANNEL, id_)


async def test_job_id_queue(redis_url):
    await asyncio.gather(assert_correct_job_ids(redis_url), publish_job_ids(redis_url))




