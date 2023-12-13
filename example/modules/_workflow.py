from virtool_workflow import Workflow

wf = Workflow()


@wf.step(name="Step One")
def step_1():
    """
    This is a description for the first step.
    """


@wf.step
def step_2():
    """
    This is a description for the second step.
    """
