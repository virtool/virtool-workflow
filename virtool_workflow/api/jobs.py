from typing import Callable, Optional, Awaitable

import aiohttp

from .errors import raising_errors_by_status_code
from ..data_model import Job, Status


async def acquire_job_by_id(job_id: str, http: aiohttp.ClientSession, jobs_api_url):
    """
    Acquire the job with a given ID using the jobs API.

    :param job_id: The id of the job to acquire
    :param http: An aiohttp.ClientSession to use to make the request.
    :param jobs_api_url: The url for the jobs API.

    :return: a :class:`virtool_workflow.data_model.Job` instance with an api key (.key attribute)
    """
    async with http.patch(f"{jobs_api_url}/jobs/{job_id}", json={"acquired": True}) as response:
        async with raising_errors_by_status_code(response) as document:
            return Job(
                id=document["id"],
                args=document["args"],
                mem=document["mem"],
                proc=document["proc"],
                status=document["status"],
                task=document["task"],
                key=document["key"],
            )


def acquire_job(http: aiohttp.ClientSession, jobs_api_url: str):
    async def _job_provider(job_id: str):
        return await acquire_job_by_id(job_id, http, jobs_api_url)

    return _job_provider


PushStatus = Callable[[str, str, str, int, Optional[str]], Awaitable[Status]]


def push_status(job_id: str, http: aiohttp.ClientSession, jobs_api_url: str) -> PushStatus:
    async def _push_status(self, state: str, stage: str, progress: int, error: str = None):
        async with http.post(f"{jobs_api_url}/jobs/{job_id}/status", json={
            "state": state,
            "stage": stage,
            "error": error,
            "progress": progress,
        }) as response:
            async with raising_errors_by_status_code(response, accept=[200]) as status_json:
                return Status(**status_json)

    return _push_status
