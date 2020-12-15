import pytest
from virtool_workflow_runtime.runtime import runtime_scope, execute
from typing import Callable


class TestRuntimeEnvironment:
    """Testing harness for Virtool Workflows."""
    def __init__(self):
        self.scope = runtime_scope

    async def execute_function(self, func: Callable):
        """Bind runtime fixtures to a function and execute it."""
        return (await self.scope.bind(func))()

    execute = execute


@pytest.yield_fixture()
def runtime():
    """The WorkflowFixtureScope which would be used by the runtime."""
    test_environment = TestRuntimeEnvironment()

    with test_environment.scope:
        return test_environment
