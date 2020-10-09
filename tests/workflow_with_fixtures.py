import pytest
from virtool_workflow.workflow_fixture import fixture
from virtool_workflow import Workflow, WorkflowExecutionContext
from virtool_workflow.context import State
from typing import Dict, Any


@fixture
def fixture_():
    return "FIXTURE"


@fixture
def state(fixture_: str):
    return dict(fixture=fixture_)


@pytest.fixture
def workflow_with_fixtures():

    test_workflow = Workflow()

    @test_workflow.startup
    def start(
            state: Dict[str, Any],
            execution_context: WorkflowExecutionContext,
            ctx: WorkflowExecutionContext,
            workflow: Workflow,
            wf: Workflow,
    ):
        state["start"] = True
        assert execution_context.state == State.STARTUP
        assert execution_context == ctx
        assert workflow == test_workflow == wf

    @test_workflow.step
    async def step(fixture_: str, state: Dict[str, Any]):
        assert state["fixture"] == fixture_
        state["step"] = True

    @test_workflow.cleanup
    def clean(state, wf):
        state["clean"] = True
        wf.results = state

    return test_workflow




