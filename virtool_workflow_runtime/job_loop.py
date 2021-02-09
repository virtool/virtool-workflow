import logging

from virtool_workflow.data_model import Job
from virtool_workflow_runtime.hooks import on_init

logger = logging.getLogger(__name__)


@on_init
def instantiate_job_container_dict(scope):
    scope["job_containers"] = {}


async def process_job(job: Job, image: str, docker, job_containers):
    job_containers[job._id] = docker.containers.run(image, detach=True)


async def job_loop(jobs, workflow_to_docker_image, scope):
    """Process incoming jobs."""
    _process_job = await scope.bind(process_job, strict=False)
    async for job in jobs:
        logger.debug(f"Processing job {job}")
        image = workflow_to_docker_image[job.task]
        await _process_job(job, image)
