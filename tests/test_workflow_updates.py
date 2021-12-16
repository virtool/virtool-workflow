from virtool_workflow._steps import WorkflowStep
from virtool_workflow.workflow import Workflow


async def this_is_a_test_step():
    """
    This is a docstring
    
    This is the second line of a docstring
    
    :return: None
    """
    ...
    

CORRECT_DESCRIPTION = (
    "This is a docstring\n"
    "\n"
    "This is the second line of a docstring\n"
)


async def test_workflow_step_from_callable():
    """Test that the display name and description are correctly interpreted."""
    step = WorkflowStep.from_callable(this_is_a_test_step)
    
    assert step.display_name == "This Is A Test Step"
    assert step.description == CORRECT_DESCRIPTION
    assert step.call is this_is_a_test_step
    
    
    assert await step() is None
