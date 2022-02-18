from virtool_workflow import Workflow
from virtool_workflow.runtime.redis import _run_job_from_redis


async def test_run_once_from_redis(create_job, redis, redis_service, base_config):
    job = await create_job({})

    list_name = f"{job['workflow']}_jobs"
    await redis.lpush(list_name, job["_id"])

    redis.close()
    await redis.wait_closed()


    workflow = Workflow()

    workflow_did_run = False

    @workflow.step
    def test_workflow(job, logger):
        nonlocal workflow_did_run
        workflow_did_run = True

    await _run_job_from_redis(list_name, redis_service, workflow, **base_config)

    assert workflow_did_run
