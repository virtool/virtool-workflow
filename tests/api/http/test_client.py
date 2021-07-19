from fixtures import FixtureScope
from virtool_workflow.api.client import authenticated_http, JobApiHttpSession
from tests.api.mocks.mock_job_routes import TEST_JOB


async def test_http_client_does_close(runtime):
    client = runtime.get_or_instantiate("client")
    assert isinstance(client, JobApiHttpSession)

    await runtime.__aexit__(None, None, None)

    assert client.client.closed


async def test_add_auth_headers_adds_auth(runtime):
    job_id = "test_job"
    job_key = "foobar"

    runtime["job_id"] = job_id
    runtime["key"] = job_key

    client = await runtime.instantiate(authenticated_http)

    assert client.auth.login == f"job-{job_id}"
    assert client.auth.password == job_key


async def test_auth_headers_applied_once_job_is_ready(runtime, http, jobs_api_url):
    runtime["http"] = http
    runtime["job_id"] = TEST_JOB["id"]
    runtime["jobs_api_url"] = jobs_api_url
    job = await runtime.get_or_instantiate("job")

    assert http.auth.login == f"job-{job.id}"
    assert http.auth.password == job.key
