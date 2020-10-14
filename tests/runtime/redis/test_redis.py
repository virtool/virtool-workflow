from virtool_workflow_runtime._redis import *
from virtool_workflow_runtime.runtime import execute_from_redis

JOB_IDs = [str(n) for n in range(3)]


async def assert_correct_job_ids():
    queue = job_id_queue()
    for id_ in JOB_IDs:
        _id = await queue.__anext__()
        assert _id == id_


async def publish_job_ids():
    async with connect() as redis:
        for id_ in JOB_IDs:
            await redis.publish(VIRTOOL_JOBS_CHANNEL, id_)


async def run_workflows_from_redis(test_workflow):
    exec_ = execute_from_redis(workflow=test_workflow)
    for _ in JOB_IDs:
        result = await exec_.__anext__()
        assert result["start"] and result["clean"]
        assert result["1"] and result["2"]


async def test_job_id_queue():
    await asyncio.gather(assert_correct_job_ids(), publish_job_ids())


async def test_execute_from_redis(test_workflow):
    await asyncio.gather(run_workflows_from_redis(test_workflow), publish_job_ids())

