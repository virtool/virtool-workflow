import sys
import traceback
from typing import Awaitable, Callable, Optional

from .context import WorkflowExecutionContext, UpdateListener, State
from .workflow import Workflow, WorkflowStep


class WorkflowError(Exception):
    """An exception ocurring during the execution of a workflow."""

    def __init__(
            self,
            cause: Exception,
            workflow: Workflow,
            context: WorkflowExecutionContext,
            *args,
            max_traceback_depth: int = 50,
            **kwargs):
        """

        :param cause: The inital exception raised
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


WorkflowErrorHandler = Callable[[WorkflowError], Awaitable[Optional[str]]]


async def _run_step(step: WorkflowStep, wf: Workflow, ctx: WorkflowExecutionContext, on_error: Optional[WorkflowErrorHandler] = None):
    ctx.error = None
    try:
        return await step(wf, ctx)
    except Exception as exception:
        error = WorkflowError(cause=exception, workflow=wf, context=ctx)
        ctx.error = error.traceback_data
        if on_error:
            return await on_error(error)
        else:
            raise error
        
async def _run_steps(steps, wf, ctx, on_error=None, on_each=None):
    for step in steps:
        if on_each:
            await on_each(wf, ctx)
        update = await _run_step(step, wf, ctx, on_error)
        await ctx.send_update(update)
            
            
async def _inc_step(wf, ctx):
    ctx.current_step += 1
    ctx.progress = float(ctx.current_step) / float(len(wf.steps))


async def execute(
        wf: Workflow,
        on_update: Optional[UpdateListener] = None,
        on_state_change: Optional[UpdateListener] = None,
        on_error: Optional[WorkflowErrorHandler] = None
):
    """
    Execute a Workflow.
    
    :param Workflow wf: the Workflow to execute
    :param on_update: An async function which is called when a step of the workflow provides an update
    :param on_state_change: An async function which is called when the WorkflowState changes
    :param on_error: An async function which is called upon any exception
    :raises WorkflowError: If any Exception occurs during execution it is caught and wrapped in
        a WorkflowError. The inital Exception is available by the `cause` attribute.
    """
    ctx = WorkflowExecutionContext(on_update=on_update, on_state_change=on_state_change)

    await ctx.set_state(State.STARTUP)
    await _run_steps(wf.on_startup, wf, ctx, on_error=on_error)
    await ctx.set_state(State.RUNNING)
    await _run_steps(wf.steps, wf, ctx, on_each=_inc_step, on_error=on_error)
    await ctx.set_state(State.CLEANUP)
    await _run_steps(wf.on_cleanup, wf, ctx, on_error=on_error)
    await ctx.set_state(State.FINISHED)
    
    return wf.results

