import pytest
import aioredis

import motor.motor_asyncio
from virtool_workflow_runtime.db import VirtoolDatabase, DATABASE_CONNECTION_URL_DEFAULT
from virtool_workflow_runtime._redis import job_id_queue, connect


JOB_IDs = ["1", "2", "3"]


@pytest.fixture
async def initialized_job_database():
    jobs: motor.motor_asyncio.AsyncIOMotorCollection = \
        VirtoolDatabase(db_conn_url=DATABASE_CONNECTION_URL_DEFAULT)["jobs"]

    for id_ in JOB_IDs:
        jobs.insert_one(dict(id=id_))

    return jobs


@pytest.fixture
def redis_address():
    return "redis://localhost:6379/1"


@pytest.fixture
async def publish(redis_address, initialized_job_database):
    redis = await aioredis.create_redis_pool(redis_address)
    channel = "channel:dispatch"

    async def publish(id: str):
        await redis.publish(channel, id)

    return publish


async def test_redis_connect(redis_address):
    async with connect(redis_address) as redis:
        info = await redis.execute("INFO", encoding="utf-8")
        print(info)
        raise


async def test_job_id_queue(publish, redis_address):
    jobs = job_id_queue(redis_address)

    for id_ in JOB_IDs:
        await publish(id_)

    _1 = await jobs.__anext__()
    assert _1 == JOB_IDs[0]
