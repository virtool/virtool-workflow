"""Main entrypoint(s) to run virtool workflows."""
import logging
from pathlib import Path
from typing import Optional

from virtool_workflow import discovery
from virtool_workflow import hooks
from virtool_workflow.analysis.runtime import AnalysisWorkflowEnvironment
from virtool_workflow.config.configuration import DBType
from virtool_workflow.config.configuration import load_config
from virtool_workflow.data_model import Job
from virtool_workflow.db.data_providers.analysis_data_provider import AnalysisDataProvider
from virtool_workflow.db.data_providers.index_data_provider import IndexDataProvider
from virtool_workflow.db.data_providers.sample_data_provider import SampleDataProvider
from virtool_workflow.db.data_providers.subtraction_data_provider import SubtractionDataProvider
from virtool_workflow.db.db import VirtoolDatabase
from virtool_workflow.db.inmemory import InMemoryDatabase
from virtool_workflow.db.mongo import VirtoolMongoDB
from virtool_workflow.environment import WorkflowEnvironment
from virtool_workflow.fixtures.scoping import workflow_fixtures
from virtool_workflow.workflow import Workflow

_database: Optional[VirtoolDatabase] = None
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
async def instantiate_database(db_type: DBType, db_name: str, db_connection_string: str,
                               direct_db_access_allowed: bool):
    global _database
    if db_type == "in-memory":
        _database = InMemoryDatabase()
    elif db_type == "mongo":
        _database = VirtoolMongoDB(db_name, db_connection_string)
    elif db_type == "proxy":
        raise NotImplementedError("Proxy database is not yet supported.")
    else:
        raise ValueError(f"{db_type} is not a supported database type.")

    await hooks.on_load_database.trigger(_database)

    if direct_db_access_allowed:
        workflow_fixtures["database"] = lambda: _database


@hooks.on_load_config
async def instantiate_job(job_id: Optional[str], mem: int, proc: int):
    jobs = await hooks.use_job.trigger()
    if jobs:
        job = next(job_ for job_ in jobs if isinstance(job_, Job))
    elif job_id:
        job_document = await _database.jobs.get(job_id)
        if not job_document:
            raise RuntimeError("No job document in database. Please supply a valid job_id.")
        job = Job(
            _id=job_document["_id"],
            args=job_document["args"],
            mem=job_document["mem"] if "mem" in job_document else mem,
            proc=job_document["proc"] if "proc" in job_document else proc,
            task=job_document["task"] if "task" in job_document else None,
        )
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

        if "analysis_id" in job.args:
            _environment.data_providers.analysis_provider = \
                AnalysisDataProvider(_database.analyses, job.args["analysis_id"])

        if "sample_id" in job.args:
            _environment.data_providers.sample_provider = \
                SampleDataProvider(job.args["sample_id"], _database.samples, _database.analyses)

        if "index_id" in job.args:
            _environment.data_providers.index_provider = \
                IndexDataProvider(job.args["index_id"], _database.indexes, _database.references)

        if "subtractions" in job.args:
            _environment.data_providers.subtraction_providers = \
                [SubtractionDataProvider(id_, _database.subtractions) for id_ in job.args["subtractions"]]
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
    result = await _environment.execute(_workflow)
    logger.debug(result)
