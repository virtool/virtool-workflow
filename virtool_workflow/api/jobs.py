import asyncio
import functools
import traceback
from logging import getLogger
from typing import Optional

from aiohttp import ClientConnectionError, ClientSession
from pyfixtures import fixture
from virtool_core.models.job import JobStatus

from virtool_workflow import WorkflowStep
from virtool_workflow.api.errors import (
    raising_errors_by_status_code,
    JobAlreadyAcquired,
    JobsAPIServerError,
)
from virtool_workflow.data_model.jobs import WFJob

logger = getLogger("api")


async def acquire_job_by_id(
    http: ClientSession,
    jobs_api_connection_string: str,
    job_id: str,
):
    """
    Acquire the job with a given ID using the jobs API.

    :param http: An aiohttp.ClientSession to use to make the request.
    :param jobs_api_connection_string: The url for the jobs API.
    :param job_id: The id of the job to acquire
    :return: a job including its API key
    """
    async with http.patch(
        f"{jobs_api_connection_string}/jobs/{job_id}", json={"acquired": True}
    ) as response:

        async with raising_errors_by_status_code(
            response, status_codes_to_exceptions={400: JobAlreadyAcquired}
        ) as resp_json:
            return WFJob(**resp_json)


@fixture
def acquire_job(http: ClientSession, jobs_api_connection_string: str):
    async def _job_provider(job_id: str, timeout=3):
        attempt = 1

        while attempt < 4:
            logger.info(f"Acquiring job: id={job_id} attempt={attempt}")

            try:
                job = await acquire_job_by_id(http, jobs_api_connection_string, job_id)
                logger.info(f"Acquired job: id={job_id}")
                return job
            except ClientConnectionError:
                await asyncio.sleep(timeout)

            attempt += 1

        raise JobsAPIServerError("Unable to connect to server.")

    return _job_provider


async def ping(http: ClientSession, jobs_api_connection_string: str, job_id: str):
    """
    Send a ping to the jobs API to indicate that the job is still running.

    :param http: An :class:`aiohttp.ClientSession` to use to make the request.
    :param jobs_api_connection_string: The url for the jobs API.
    :param job_id: The id of the job to ping.
    :return: The job.
    """
    print(http)

    async with http.put(f"{jobs_api_connection_string}/jobs/{job_id}/ping") as resp:
        print(resp.status)
        print(await resp.text())

    print("PING")

    logger.info("Sent ping")


@fixture(scope="function")
async def push_status(
    http,
    job: WFJob,
    jobs_api_connection_string: str,
    error: Optional[Exception],
    progress: float,
    current_step: WorkflowStep,
):
    return functools.partial(
        _push_status,
        http,
        job,
        jobs_api_connection_string,
        step_name=current_step.display_name if current_step is not None else None,
        step_description=(
            current_step.description if current_step is not None else None
        ),
        stage=(current_step.function.__name__ if current_step is not None else None),
        progress=progress,
        error=error,
    )


async def _push_status(
    http,
    job: WFJob,
    jobs_api_connection_string: str,
    step_name: str,
    step_description: str,
    stage: str,
    state: str,
    progress: float,
    error: Optional[Exception] = None,
    max_tb: int = 50,
):

    payload = {
        "state": state,
        "stage": stage,
        "step_name": step_name,
        "step_description": step_description,
        "error": {
            "type": error.__class__.__name__,
            "traceback": traceback.format_tb(error.__traceback__, max_tb),
            "details": [str(arg) for arg in error.args],
        }
        if error is not None
        else None,
        "progress": int(progress * 100),
    }

    logger.info(f"Reported status: step={step_name} state={state}")

    async with http.post(
        f"{jobs_api_connection_string}/jobs/{job.id}/status", json=payload
    ) as response:
        async with raising_errors_by_status_code(
            response, accept=[200, 201]
        ) as status_json:
            return JobStatus(**status_json)
