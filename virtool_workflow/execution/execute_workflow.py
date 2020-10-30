"""Execute workflows without runtime related hooks (database, redis, etc.)."""
import sys
import traceback
from typing import Awaitable, Callable, Optional, Dict, Any

from virtool_workflow.execution.context import WorkflowExecutionContext, State
from virtool_workflow.workflow import Workflow, WorkflowStep
from virtool_workflow.fixtures.scope import WorkflowFixtureScope
from virtool_workflow.execution.hooks import hook


class WorkflowError(Exception):
    """An exception occurring during the execution of a workflow."""

    def __init__(
            self,
            cause: Exception,
            workflow: Workflow,
            context: WorkflowExecutionContext,
            max_traceback_depth: int = 50
    ):
        """

        :param cause: The initial exception raised
        :param workflow: The workflow object being executed
        :param context: The execution context of the workflow being executed
        :param max_traceback_depth: The maximum depth for the traceback data
        """
        self.cause = cause
        self.workflow = workflow
        self.context = context

        exception, value, trace_info = sys.exc_info()

        self.traceback_data = {
            "type": exception.__name__,
            "traceback": traceback.format_tb(trace_info, max_traceback_depth),
            "details": [str(arg) for arg in value.args]
        }

        super().__init__(str(cause))


@hook
def on_workflow_error(error: WorkflowError) -> Optional[str]:
    pass


@hook
def on_step(workflow: Workflow, context: WorkflowExecutionContext):
    pass


async def _run_step(
        step: WorkflowStep,
        workflow: Workflow,
        ctx: WorkflowExecutionContext,
):
    ctx.error = None
    try:
        return [await step()]
    except Exception as exception:
        error = WorkflowError(cause=exception, workflow=workflow, context=ctx)
        ctx.error = error.traceback_data

        callback_results = await on_workflow_error.trigger(error)

        if callback_results:
            return callback_results

        raise error from exception


async def _run_steps(steps, workflow, ctx):
    for step in steps:
        update = await _run_step(step, workflow, ctx)
        await on_step.trigger(workflow, ctx)
        await ctx.send_update(*update)


@on_step.callback
def _inc_step(workflow, ctx):
    ctx.current_step += 1
    ctx.progress = float(ctx.current_step) / float(len(workflow.steps))


async def execute(
        _wf: Workflow,
        _context: WorkflowExecutionContext = None,
        scope: WorkflowFixtureScope = None,
) -> Dict[str, Any]:
    """
    Execute a Workflow.

    :param Workflow _wf: the Workflow to execute
    :param _context: The WorkflowExecutionContext to start from
    :param scope: The WorkflowFixtureScope to use for fixture injection
    :raises WorkflowError: If any Exception occurs during execution it is caught and wrapped in
        a WorkflowError. The initial Exception is available by the `cause` attribute.
    """
    _context = _context if _context else WorkflowExecutionContext()

    scope = scope if scope else WorkflowFixtureScope()
    with scope as execution_scope:

        execution_scope.add_instance(_wf, "wf", "workflow")
        execution_scope.add_instance(_context, "context", "execution_context", "ctx")
        execution_scope.add_instance({}, "result", "results")

        bound = await execution_scope.bind_to_workflow(_wf)

        await _context.set_state(State.STARTUP)
        await _run_steps(bound.on_startup, bound, _context)
        await _context.set_state(State.RUNNING)
        await _run_steps(bound.steps, bound, _context)
        await _context.set_state(State.CLEANUP)
        await _run_steps(bound.on_cleanup, bound, _context)
        await _context.set_state(State.FINISHED)

        return scope["result"]
