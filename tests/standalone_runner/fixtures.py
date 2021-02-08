import pytest

from virtool_workflow_runtime.cli import main


@pytest.fixture
def loopless_main(monkeypatch):
    async def mock_job_loop():
        ...

    monkeypatch.setattr("virtool_workflow_runtime.cli.job_loop", mock_job_loop)

    return main
