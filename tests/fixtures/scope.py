import pytest
from virtool_workflow import WorkflowFixtureScope


@pytest.yield_fixture()
def empty_scope():
    with WorkflowFixtureScope() as scope:
        yield scope
