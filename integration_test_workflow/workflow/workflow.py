import logging
from integration_test_workflows import (
    test_hmms,
    test_indexes,
    test_sample,
    test_subtractions,
)
from virtool_workflow import features, hooks, fixture
from virtool_workflow.analysis.features.trimming import Trimming
from virtool_workflow.decorator_api import collect, step
from virtool_workflow.execution.run_in_executor import FunctionExecutor
from virtool_workflow.execution.run_subprocess import RunSubprocess
from virtool_workflow.execution.workflow_execution import WorkflowExecution
from virtool_workflow.workflow import Workflow
from virtool_workflow.workflow_feature.merge_workflows import MergeWorkflows

features.install(
    Trimming(),
    MergeWorkflows(test_hmms, test_indexes, test_sample, test_subtractions,),
)


@fixture
def logger():
    return logging.getLogger(__name__)


@hooks.on_update
def log_updates(update, logger):
    logger.info(f"Sent update: {update}")


@step
def test_results_available(results):
    assert results is not None
    assert isinstance(results, dict)
    return "Results fixture available"


@step
def test_builtin_fixtures_available(workflow, run_in_executor, run_subprocess):
    assert isinstance(workflow, Workflow)
    assert isinstance(run_in_executor, FunctionExecutor)
    assert isinstance(run_subprocess, RunSubprocess)
    return "Builtin fixtures available"


@step
async def test_execution_fixture(execution):
    assert isinstance(execution, WorkflowExecution)

    updates = []

    @hooks.on_update
    def follow_updates(update):
        updates.append(update)

    await execution.send_update("UPDATE")

    assert "UPDATE" in updates

    return "`execution.send_update()` working"
