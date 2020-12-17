from typing import Iterable
from virtool_workflow.fixtures.scope import WorkflowFixtureScope
from virtool_workflow_runtime import discovery


class InitializedWorkflowFixtureScope(WorkflowFixtureScope):
    """A WorkflowFixtureScope that imports fixtures from a set of modules upon `__enter__`."""
    def __init__(self, fixture_plugins: Iterable[str]):
        self.fixture_plugins = fixture_plugins
        super().__init__()

    def __enter__(self):
        discovery.load_fixture_plugins(self.fixture_plugins)
        return super(InitializedWorkflowFixtureScope, self).__enter__()

