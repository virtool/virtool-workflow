from virtool_workflow import Workflow

my_workflow = Workflow()


@my_workflow.startup
async def run_on_startup():
    ...


@my_workflow.step
async def first_workflow_step():
    ...


@my_workflow.step
async def second_workflow_step():
    ...


@my_workflow.cleanup
async def run_on_completion_of_steps():
    ...