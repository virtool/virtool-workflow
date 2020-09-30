from .workflow import Workflow, WorkflowStep
from .context import Context, UpdateListener, State

class WorkflowError(Exception):
    """An exception ocurring during the execution of a workflow"""

    def __init__(self, cause: Exception, workflow: Workflow, context: Context, *args, **kwargs):
        """
        :param cause: The inital exception raised 
        :param workflow: The workflow object being executed 
        :param context: The execution context of the workflow being executed
        """
        self.cause = cause
        self.workflow = workflow
        self.context = context


WorkflowErrorHandler = Callable[[WorkflowError], Awaitable[Optional[str]]]


async def __run_step(step: WorkflowStep, wf: Workflow, ctx: Context, on_error: WorkflowErrorHandler):
    try:
        return await step(wf, ctx)
    except Exception as exception:
        if on_error:
            return await on_error(wf, ctx, exception)
        else:
            raise WorkflowError(cause=exception, workflow=wf, context=ctx)
        
async def __run_steps(steps, wf, ctx, on_error, on_each=None):
    for step in steps:
        update = await __run_step(step, wf, ctx, on_error)
        if update:
            ctx.send_update(update)
        if on_each:
            on_each(wf, ctx)


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
    ctx = Context(on_update=on_update, on_state_change=on_state_change)
    
    
    ctx.state = State.STARTUP
    __run_steps(wf.on_startup)
    ctx.state = State.RUNNING
    __run_steps(wf.steps)
    ctx.state = State.CLEANUP
    __run_steps(wf.on_cleanup, on_each = lambda wf, ctx: ctx.current_step.__add__(1))
    ctx.state = State.FINISHED

