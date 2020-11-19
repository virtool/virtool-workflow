"""An example workflow which uses workflow fixtures."""
from typing import Dict, Any

import pytest

from virtool_workflow import Workflow, WorkflowExecution, State, fixture


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
            execution: WorkflowExecution,
            workflow: Workflow,
    ):
        state["start"] = True
        assert execution.state == State.STARTUP
        assert workflow == test_workflow

    @test_workflow.step
    async def step(fixture_: str, state: Dict[str, Any]):
        assert state["fixture"] == fixture_
        state["step"] = True

    @test_workflow.cleanup
    def clean(state, results):
        state["clean"] = True
        results.update(state)

    return test_workflow
