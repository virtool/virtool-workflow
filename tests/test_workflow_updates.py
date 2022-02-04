import pytest
import asyncio
from virtool_workflow._steps import WorkflowStep
from virtool_workflow import execute, Workflow
from virtool_workflow.execution import states
from fixtures import FixtureScope, fixture, runs_in_new_fixture_context


async def this_is_a_test_step():
    """
    This is a docstring
    
    This is the second line of a docstring
    
    :return: None
    """
    ...
    

CORRECT_DESCRIPTION = "This is a docstring"


async def test_workflow_step_from_callable():
    """Test that the display name and description are correctly interpreted."""
    step = WorkflowStep.from_callable(this_is_a_test_step)
    
    assert step.display_name == "This Is A Test Step"
    assert step.description == CORRECT_DESCRIPTION
    assert step.function is this_is_a_test_step
    
    assert await step() is None


@pytest.fixture
def workflow():
    wf = Workflow()

    @wf.step
    def step_1():
        """Description for step 1"""

    @wf.step
    def step_2():
        """Description for step 2"""

    return wf
