import pytest
from importlib import import_module
from fixtures import FixtureScope
from virtool_workflow.runtime.runtime import run_workflow



@pytest.fixture
async def base_config(job_id, jobs_api):
    return {
        "mem": 8,
        "proc": 2,
        "job_id": job_id,
        "jobs_api_url": jobs_api
    }


@pytest.fixture
async def exec_workflow(base_config):
    import_module("virtool_workflow.builtin_fixtures")
    import_module("virtool_workflow.runtime.providers")
    import_module("virtool_workflow.analysis.fixtures")

    async def _exec_workflow(workflow, **kwargs):
        base_config.update(kwargs)
        await run_workflow(workflow, base_config)

    return _exec_workflow


