from virtool_workflow.analysis import fixtures as analysis_fixtures
from virtool_workflow.config import fixtures as config
from virtool_workflow.execution.run_in_executor import run_in_executor, thread_pool_executor
from virtool_workflow.execution.run_subprocess import run_subprocess
from virtool_workflow.fixtures import FixtureGroup
from virtool_workflow.runtime.providers import providers

workflow = FixtureGroup(
    config.work_path,
    config.data_path,
    run_in_executor,
    thread_pool_executor,
    run_subprocess,
    providers["job"],
    mem=lambda job: job.mem,
    proc=lambda job: job.proc
)
"""A :class:`FixtureGroup` containing all fixtures available within workflows."""

analysis = FixtureGroup(**providers,
                        **{k: getattr(analysis_fixtures, k)
                           for k in analysis_fixtures.__all__})
"""A :class:`FixtureGroup` containing all fixtures excusive to analysis workflows."""

runtime = FixtureGroup(**providers)
"""A :class:`FixtureGroup` containing all fixtures available to the runtime."""
