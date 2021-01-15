import pytest
from virtool_workflow import FixtureScope


@pytest.yield_fixture()
def empty_scope():
    with FixtureScope() as scope:
        yield scope
