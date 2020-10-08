import pytest
from virtool_workflow.workflow_fixture import workflow_fixture, WorkflowFixture
from virtool_workflow import Workflow, WorkflowExecutionContext
from virtool_workflow.context import State
from typing import Dict, Any


@workflow_fixture
def fixture():
    return "FIXTURE"

@workflow_fixture
def state(fixture: str):
    return dict(fixture=fixture)


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
    async def step(fixture: str, state: Dict[str, Any]):
        assert state["fixture"] == fixture
        state["step"] = True

    @test_workflow.cleanup
    def clean(state, wf):
        state["clean"] = True
        wf.results = state

    return test_workflow




