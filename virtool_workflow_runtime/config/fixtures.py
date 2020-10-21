"""Fixtures for getting runtime configuration details."""
from virtool_workflow import fixture


@fixture
def number_of_processes() -> int:
    """The number of allowable processes for the currently executed workflow/job."""
    # TODO: load virtool config
    return 3
