import logging

from virtool_workflow.data_model import Job
from virtool_workflow_runtime.hooks import on_exit

logger = logging.getLogger(__name__)


async def process_job(job: Job, image: str, command: str, docker, job_containers):
    job_containers[job] = docker.containers.run(image, command, detach=True)


async def job_loop(jobs, workflow_to_docker_image, scope):
    """Process incoming jobs."""
    _process_job = await scope.bind(process_job, strict=False)
    async for job in jobs:
        logger.debug(f"Processing job {job}")
        image = workflow_to_docker_image[job.task]
        await _process_job(job, image)


@on_exit
def stop_all_containers(job_containers):
    for container in job_containers.values():
        container.stop()
