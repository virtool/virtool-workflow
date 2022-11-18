"""Test utilities for Virtool Workflows."""
from importlib import import_module
from typing import Callable

import pytest

from pyfixtures import FixtureScope, fixture
from virtool_workflow import Workflow, execute
from virtool_workflow.runtime.events import Events

import_module("virtool_workflow.builtin_fixtures")
import_module("virtool_workflow.analysis.fixtures")


@fixture
def config():
    return {
        "proc": 2,
        "mem": 8,
    }


class WorkflowTestRunner(FixtureScope):
    async def execute(self, workflow: Workflow = None):
        if workflow is None:
            workflow = self["workflow"]

        async with FixtureScope() as scope:
            await execute(workflow, scope, Events())

            return await scope.get_or_instantiate("results")

    async def execute_function(self, func: Callable, **kwargs):
        bound = await self.bind(func, **kwargs)
        await bound()


@pytest.fixture
async def runtime(http, jobs_api_connection_string):
    async with WorkflowTestRunner() as _runtime:
        _runtime["config"] = {
            "work_path": "temp",
            "mem": 8,
            "proc": 2,
        }
        _runtime["job_id"] = "test_job"
        _runtime["http"] = http
        _runtime["jobs_api_connection_string"] = jobs_api_connection_string
        yield _runtime


def install_as_pytest_fixtures(_globals, *fixtures):
    """Create pytest fixtures for each fixture in a given :class:`FixtureGroup`."""
    for _fixture in fixtures:
        _globals[fixture.__name__] = pytest.fixture(_fixture)


__all__ = ["runtime", "install_as_pytest_fixtures"]
