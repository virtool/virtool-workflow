import arrow
from aiohttp.web import json_response, View, RouteTableDef
from virtool_core.models.job import JobStatus, JobState

from tests.fixtures.api.utils import custom_dumps, generate_not_found
from virtool_workflow.pytest_plugin.data import Data


def create_jobs_routes(data: Data):
    routes = RouteTableDef()

    @routes.view("/jobs/{job_id}")
    class JobView(View):
        async def patch(self):
            """Endpoint for testing job acquisition."""

            json = await self.request.json()

            if json.get("acquired") is not True:
                return json_response(
                    {"id": "bad_request", "message": "Bad request"}, status=400
                )

            data.job.acquired = True
            data.job.status.append(
                JobStatus(
                    progress=0, state=JobState.PREPARING, timestamp=arrow.utcnow().naive
                )
            )

            return json_response(
                data.job.dict(),
                status=200,
                dumps=custom_dumps,
            )

    @routes.view("/jobs/{job_id}/ping")
    class JobPingView(View):
        async def put(self):
            print(self.request.headers["Authorization"])

            job_id = self.request.match_info["job_id"]

            if job_id != data.job.id:
                return generate_not_found()

            data.job.ping.pinged_at = arrow.utcnow().naive

            return json_response(data.job.ping.dict(), status=200, dumps=custom_dumps)

    @routes.view("/jobs/{job_id}/status")
    class JobStatusView(View):
        async def post(self):
            job_id = self.request.match_info["job_id"]

            if job_id != data.job.id:
                return generate_not_found()

            status = JobStatus(
                **{
                    **(await self.request.json()),
                    **{"timestamp": arrow.utcnow().naive.isoformat()},
                }
            )

            data.job.status.append(status)

            return json_response(status.dict(), status=201, dumps=custom_dumps)

    return routes
