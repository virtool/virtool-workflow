from virtool_workflow.api.client import authenticated_http
from tests.api.mocks.mock_job_routes import TEST_JOB


async def test_add_auth_headers_adds_auth(runtime):
    job_id = "test_job"
    job_key = "foobar"

    runtime["job_id"] = job_id
    runtime["key"] = job_key

    client = await runtime.instantiate(authenticated_http)

    assert client.auth.login == f"job-{job_id}"
    assert client.auth.password == job_key


async def test_auth_headers_applied_once_job_is_ready(
    runtime, http, jobs_api_connection_string
):
    runtime["http"] = http
    runtime["job_id"] = TEST_JOB["id"]
    runtime["jobs_api_connection_string"] = jobs_api_connection_string
    job = await runtime.get_or_instantiate("job")

    assert http.auth.login == f"job-{job.id}"
    assert http.auth.password == job.key
