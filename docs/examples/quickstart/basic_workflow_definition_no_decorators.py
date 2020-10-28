from virtool_workflow import Workflow


def run_on_startup():
    ...


def first_workflow_step():
    ...


def second_workflow_step():
    ...


def run_on_completion_of_steps():
    ...


my_workflow = Workflow(
    startup=[run_on_startup],
    steps=[first_workflow_step, second_workflow_step],
    cleanup=[run_on_completion_of_steps],
)

# or

my_workflow = Workflow()
my_workflow.on_startup.append(run_on_startup)
my_workflow.steps.append(first_workflow_step)
my_workflow.steps.append(second_workflow_step)
my_workflow.on_cleanup.append(run_on_completion_of_steps)