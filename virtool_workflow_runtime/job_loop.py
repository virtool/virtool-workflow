import logging
from typing import List

from virtool_workflow.data_model import Job
from virtool_workflow_runtime._docker import start_workflow_container
from virtool_workflow_runtime.hooks import on_exit, on_container_exit, on_job_cancelled

logger = logging.getLogger(__name__)


async def job_is_finished(job) -> bool:
    logger.warning(f"function {job_is_finished} is not implemented.")
    return True


async def process_job(job: Job, image: str, args: List[str], docker, containers):
    container = await start_workflow_container(docker, containers, image, *args)

    @on_job_cancelled
    async def stop_container_when_job_is_cancelled(job_id):
        if job_id == job._id:
            container.stop()

    @on_container_exit(container)
    async def _handle_container_failure():
        if not await job_is_finished(job):
            await process_job(job, image, args, docker, containers)


async def job_loop(jobs, workflow_to_docker_image, scope):
    """Process incoming jobs."""
    _process_job = await scope.bind(process_job, strict=False)
    async for job in jobs:
        logger.debug(f"Processing job {job}")
        image = workflow_to_docker_image[job.task]
        await _process_job(job, image, [])


@on_exit
def stop_all_containers(containers):
    for container in containers.values():
        container.stop()
