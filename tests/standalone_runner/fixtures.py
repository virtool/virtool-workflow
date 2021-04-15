import pytest
import functools

from virtool_workflow_runtime.cli import main


@pytest.fixture
def loopless_main(monkeypatch, redis_service):
    async def mock_job_loop():
        ...

    monkeypatch.setattr("virtool_workflow_runtime.cli.job_loop", mock_job_loop)

    return functools.partial(main, redis_connection_string=redis_service)
