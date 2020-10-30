from virtool_workflow.execution.hooks import hook
from virtool_workflow import Workflow, WorkflowExecutionContext


@hook
def on_error(error: Exception, workflow: Workflow, context: WorkflowExecutionContext):
    pass


@hook
def on_finish():
    pass


@hook
def on_failure():
    pass


@hook
def on_success():
    pass


