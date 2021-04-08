from virtool_workflow import hooks
from virtool_workflow.fixtures.scope import FixtureScope
from virtool_workflow.fixtures.workflow_fixture import workflow_fixtures

workflow_scope = FixtureScope(workflow_fixtures)
"""The :class:`FixtureScope` to be used for workflow runs."""


@hooks.on_finalize
async def _close_scopes():
    """Close :class:`FixtureScope` instances when the workflow finishes."""
    await workflow_scope.close()
