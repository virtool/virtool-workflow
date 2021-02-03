from typing import Iterable

from virtool_workflow import discovery
from virtool_workflow.fixtures.scope import FixtureScope


class InitializedWorkflowFixtureScope(FixtureScope):
    """A WorkflowFixtureScope that imports fixtures from a set of modules upon `__enter__`."""

    def __init__(self, fixture_plugins: Iterable[str], *providers, **instances):
        self.fixture_plugins = fixture_plugins
        super().__init__(*providers, **instances)

    def __enter__(self):
        discovery.load_fixture_plugins(self.fixture_plugins)
        return super(InitializedWorkflowFixtureScope, self).__enter__()
