import pytest
from virtool_workflow_runtime.runtime import runtime_scope


@pytest.yield_fixture()
def runtime():
    """The WorkflowFixtureScope which would be used by the runtime."""
    with runtime_scope as scope:
        yield scope
