import asyncio
import logging
from typing import List

from virtool_workflow.data_model import Job
from virtool_workflow_runtime._docker import start_workflow_container
from virtool_workflow_runtime.hooks import on_exit, on_container_exit, on_job_cancelled, on_job_processed, \
    on_job_finished

logger = logging.getLogger(__name__)


async def job_is_finished(job) -> bool:
    logger.warning(f"function {job_is_finished} is not implemented.")
    return True


async def process_job(job: Job, image: str, args: List[str], docker, containers, scope):
    """
    Process a job.

    1. Start the job's associated workflow container
    2. Set handlers for events relating to that container
    3. Trigger `on_job_processed` hook
    """
    container = await start_workflow_container(docker, containers, image, *args)

    container_finished_future = asyncio.get_running_loop().create_future()

    @on_job_cancelled
    async def stop_container_when_job_is_cancelled(id_):
        if id_ == job.id:
            logger.debug(f"Stopping {container} running {container.image} due to cancellation of {id_}.")
            container.stop(timeout=3)

    @on_container_exit(container)
    async def _handle_container_failure():
        container_exit = container.wait()
        logger.info(f"{container} exited with status code: {container_exit['StatusCode']}")
        container_finished_future.set_result(container_exit)

    await on_job_processed.trigger(scope, job)

    await container_finished_future

    await on_job_finished.trigger(scope, job)


async def job_loop(jobs, workflow_to_docker_image, scope):
    """Process incoming jobs."""
    _process_job = await scope.bind(process_job, strict=False)
    async for job in jobs:
        logger.info(f"Processing job {job}")
        image = workflow_to_docker_image[job.task]
        await _process_job(job, image, [])


@on_exit
def stop_all_containers(containers):
    for container in containers.values():
        container.stop()
