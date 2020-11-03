from virtool_workflow import Hook, Workflow, WorkflowError, WorkflowFixtureScope
from typing import Dict, Any

on_success = Hook("on_success", parameters=[Workflow, Dict[str, Any]], return_type=None)
on_failure = Hook("on_failure", parameters=[WorkflowError], return_type=None)
on_finish = Hook("on_finish", parameters=[Workflow], return_type=None)


@on_success
async def _trigger_on_finish_from_on_success(workflow: Workflow, _):
    await on_finish.trigger(workflow)


@on_failure
async def _trigger_on_finish_from_on_failure(error: WorkflowError):
    await on_finish.trigger(error.workflow)


on_load_fixtures = Hook("on_load_fixtures", [WorkflowFixtureScope], return_type=None)







