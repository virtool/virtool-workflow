import aiohttp

from .scope import api_fixtures
from ..data_model import Job


@api_fixtures.fixture
def job_provider(http_client: aiohttp.ClientSession, jobs_api_url: str):
    async def _job_provider(job_id: str):
        async with http_client.patch(f"{jobs_api_url}/jobs/{job_id}", json={"acquired": True},
                                     headers={"Content-Type": "application/json"}) as response:
            document = await response.json()

            return Job(
                id=document["id"],
                args=document["args"],
                mem=document["mem"],
                proc=document["proc"],
                status=document["status"],
                task=document["task"],
                key=document["key"],
            )

    return _job_provider
