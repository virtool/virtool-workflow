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



@runs_in_new_fixture_context()
async def test_does_push_step_updates(workflow):
    step1_update = asyncio.Future()
    step2_update = asyncio.Future()
    complete_update = asyncio.Future()

    @fixture(scope="function")
    async def push_status(error, current_step, step_number):

        async def _push_status(state):
            if step_number == 1:
                assert current_step.display_name == "Step 1"
                step1_update.set_result(True)
            elif step_number == 2:
                assert current_step.display_name == "Step 2"
                step2_update.set_result(True)
            elif current_step is None:
                assert state == states.WAITING or state == states.COMPLETE
            else:
                raise ValueError("Invalid current step")

            if state == states.COMPLETE:
                complete_update.set_result(True)


        return push_status

    async with FixtureScope() as scope:
        await execute(workflow, scope)

        assert step1_update.done() is True
        assert step2_update.done() is True
        assert complete_update.done() is True



