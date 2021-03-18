from pathlib import Path

from virtool_workflow import features, Workflow
from virtool_workflow.environment import WorkflowEnvironment
from virtool_workflow.runtime import runtime

TEST_WORKFLOW_PATH = Path(__file__).parent / "runtime/workflow.py"


class MockFeature(features.WorkflowFeature):

    async def __modify_workflow__(self, workflow: Workflow) -> Workflow:
        @workflow.step
        def foo():
            ...

        return workflow

    async def __modify_environment__(self, environment: WorkflowEnvironment):
        @environment.fixture
        def bar():
            return "bar"


async def test_workflow_features_are_installable():
    features.install(MockFeature())

    environment = WorkflowEnvironment()
    environment["workflow"] = Workflow()
    await features.install_into_environment(environment)

    assert len(environment["workflow"].steps) == 1
    assert await environment.get_or_instantiate("bar") == "bar"


async def test_features_get_installed():
    features.install(MockFeature())
    async with runtime.prepare_environment(workflow_file_path=TEST_WORKFLOW_PATH) as (environment, workflow):
        assert len(environment["workflow"].steps) == 2
        assert await environment.get_or_instantiate("bar") == "bar"
