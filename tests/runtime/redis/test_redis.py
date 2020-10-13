import pytest
import aioredis
import asyncio

import motor.motor_asyncio
from virtool_workflow_runtime.db import VirtoolDatabase, DATABASE_CONNECTION_URL_DEFAULT
from virtool_workflow_runtime._redis import *

JOB_IDs = [str(n) for n in range(3)]


async def assert_correct_job_ids():
    queue = job_id_queue()
    for id_ in JOB_IDs:
        _id = await queue.__anext__()
        assert _id.decode("utf-8") == id_


async def publish_job_ids():
    async with connect() as redis:
        for id_ in JOB_IDs:
            redis.publish(VIRTOOL_JOBS_CHANNEL, id_)


async def test_job_id_queue():
    await asyncio.gather(assert_correct_job_ids(), publish_job_ids())




