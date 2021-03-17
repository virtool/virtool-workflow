from virtool_workflow.analysis import fixtures as analysis_fixtures
from virtool_workflow.config import fixtures as config
from virtool_workflow.environment import WorkflowEnvironment
from virtool_workflow.execution.run_in_executor import run_in_executor, thread_pool_executor
from virtool_workflow.execution.run_subprocess import run_subprocess
from virtool_workflow.fixtures import FixtureGroup
from virtool_workflow.results import results
from virtool_workflow.runtime.providers import providers

_workflow_fixtures = [
    results,
    config.work_path,
    config.data_path,
    run_in_executor,
    thread_pool_executor,
    run_subprocess,
]

workflow = FixtureGroup(
    *_workflow_fixtures,
    providers["job"],
    mem=lambda job: job.mem,
    proc=lambda job: job.proc
)
"""A :class:`FixtureGroup` containing all fixtures available within workflows."""

analysis = FixtureGroup(
    *_workflow_fixtures,
    **providers,
    **{k: getattr(analysis_fixtures, k)
       for k in analysis_fixtures.__all__}
)
"""A :class:`FixtureGroup` containing all fixtures excusive to analysis workflows."""

runtime = FixtureGroup(**analysis)
"""A :class:`FixtureGroup` containing all fixtures available to the runtime."""


@runtime.fixture
def environment(is_analysis_workflow: bool):
    return WorkflowEnvironment(analysis) if is_analysis_workflow else WorkflowEnvironment(workflow)
