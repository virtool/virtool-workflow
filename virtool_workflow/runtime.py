"""Main entrypoint(s) to run virtool workflows."""
import logging
from pathlib import Path
from typing import Optional

from virtool_workflow import discovery
from virtool_workflow import hooks
from virtool_workflow.abc.data_providers.jobs import JobProviderProtocol
from virtool_workflow.analysis.runtime import AnalysisWorkflowEnvironment
from virtool_workflow.config.configuration import load_config
from virtool_workflow.data_model import Job
from virtool_workflow.environment import WorkflowEnvironment
from virtool_workflow.fixtures.scoping import workflow_fixtures
from virtool_workflow.workflow import Workflow

_environment: Optional[WorkflowEnvironment] = None
_workflow: Optional[Workflow] = None
_job: Optional[Job] = None

logger = logging.getLogger(__name__)


@hooks.on_load_config
def set_log_level_to_debug(dev_mode: bool):
    if dev_mode:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)


@hooks.on_load_config
async def instantiate_job(job_id: Optional[str], mem: int, proc: int, job_provider: JobProviderProtocol = None):
    job = next(job_ for job_ in await hooks.use_job.trigger() if job_)
    if not job:
        if job_id and job_provider:
            job = await job_provider(job_id, mem=mem, proc=proc)
        else:
            raise RuntimeError("No job_id provided.")

    global _job
    _job = job

    workflow_fixtures["mem"] = lambda: job.mem
    workflow_fixtures["proc"] = lambda: job.proc


@hooks.on_load_config
async def instantiate_environment(is_analysis_workflow: bool):
    global _environment
    global _job
    job = _job
    if is_analysis_workflow:
        _environment = AnalysisWorkflowEnvironment(job)
    else:
        _environment = WorkflowEnvironment(job)


@hooks.on_load_config
def load_scripts(init_file: Path, fixtures_file: Path):
    if init_file.exists():
        discovery.import_module_from_file(module_name=init_file.name.rstrip(".py"), path=init_file)
    if fixtures_file.exists():
        discovery.import_module_from_file(module_name=fixtures_file.name.rstrip(".py"), path=fixtures_file)


@hooks.on_load_config
def extract_workflow(workflow_file_path: Path):
    global _workflow
    _workflow = discovery.discover_workflow(workflow_file_path)
    if not _workflow:
        raise RuntimeError(f"{workflow_file_path.name} does not contain a Workflow.")


async def start(**config):
    await load_config(**config)
    async with _environment:
        result = await _environment.execute(_workflow)
        logger.debug(result)
