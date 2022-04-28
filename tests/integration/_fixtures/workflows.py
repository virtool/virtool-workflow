from importlib import import_module
from typing import Dict, Any

import pytest

from virtool_workflow._runtime import run_workflow
from virtool_workflow.events import Events


@pytest.fixture
async def base_config(jobs_api):
    return {"mem": 8, "proc": 2, "jobs_api_url": jobs_api}


@pytest.fixture
async def exec_workflow(base_config: Dict[str, Any], job_id):
    import_module("virtool_workflow.builtin_fixtures")
    import_module("virtool_workflow.runtime.providers")
    import_module("virtool_workflow.analysis.fixtures")

    async def _exec_workflow(workflow, **kwargs):
        base_config.update(kwargs)
        await run_workflow(base_config, job_id, workflow, Events())

    return _exec_workflow
