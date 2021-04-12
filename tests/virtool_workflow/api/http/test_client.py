import aiohttp
import pytest

from virtool_workflow.api.client import authenticated_http, JobApiHttpSession
from virtool_workflow.api.scope import api_scope
from virtool_workflow.runtime import fixtures
from virtool_workflow.fixtures.scope import FixtureScope
from tests.virtool_workflow.api.mocks.mock_job_routes import TEST_JOB


@pytest.fixture
async def client():
    return await api_scope.get_or_instantiate("http")


async def test_http_client_does_close(client):
    assert isinstance(client, JobApiHttpSession)

    await api_scope.close()

    assert client.client.closed


async def test_add_auth_headers_adds_auth():
    job_id = "test_job"
    job_key = "foobar"

    api_scope["job_id"] = job_id
    api_scope["key"] = job_key

    client = await api_scope.instantiate(authenticated_http)

    assert client.auth.login == f"job-{job_id}"
    assert client.auth.password == job_key


async def test_auth_headers_applied_once_job_is_ready(http, jobs_api_url):
    async with FixtureScope(fixtures.workflow) as scope:
        scope["http"] = http
        scope["job_id"] = TEST_JOB["id"]
        scope["jobs_api_url"] = jobs_api_url
        job = await scope.get_or_instantiate("job")

        assert http.auth.login == f"job-{job.id}"
        assert http.auth.password == job.key
