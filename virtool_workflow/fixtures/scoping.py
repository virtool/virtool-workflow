from virtool_workflow import hooks
from virtool_workflow.fixtures.scope import FixtureScope
from virtool_workflow.fixtures.workflow_fixture import workflow_fixtures

workflow_scope = FixtureScope(workflow_fixtures)
"""The :class:`FixtureScope` to be used for workflow runs."""


@hooks.on_finish
def _close_workflow_scope_on_finish():
    """Close the workflow :class:`FixtureScope` when the workflow finishes."""
    workflow_scope.close()
