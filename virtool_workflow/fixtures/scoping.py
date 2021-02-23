from virtool_workflow import hooks
from virtool_workflow.fixtures.scope import FixtureScope
from virtool_workflow.fixtures.workflow_fixture import workflow_fixtures

workflow_scope = FixtureScope(workflow_fixtures)
"""The :class:`FixtureScope` to be used for workflow runs."""

api_scope = FixtureScope()
"""The :class:`FixtureScope` which contains the `aiohttp` client."""


@hooks.on_finish
def _close_scopes():
    """Close :class:`FixtureScope` instances when the workflow finishes."""
    workflow_scope.close()
    api_scope.close()
