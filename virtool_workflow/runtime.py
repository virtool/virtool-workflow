"""Main entrypoint(s) to run virtool workflows."""
import logging
from typing import Optional

from virtool_workflow import hooks
from virtool_workflow.analysis.runtime import AnalysisWorkflowEnvironment
from virtool_workflow.config.configuration import DBType
from virtool_workflow.data_model import Job
from virtool_workflow.db.data_providers.analysis_data_provider import AnalysisDataProvider
from virtool_workflow.db.data_providers.index_data_provider import IndexDataProvider
from virtool_workflow.db.data_providers.sample_data_provider import SampleDataProvider
from virtool_workflow.db.data_providers.subtraction_data_provider import SubtractionDataProvider
from virtool_workflow.db.db import VirtoolDatabase
from virtool_workflow.db.inmemory import InMemoryDatabase
from virtool_workflow.db.mongo import VirtoolMongoDB
from virtool_workflow.environment import WorkflowEnvironment
from virtool_workflow.fixtures.scope import FixtureScope

_database: Optional[VirtoolDatabase] = None
_environment = None


@hooks.on_load_config
def set_log_level_to_debug(dev_mode: bool):
    if dev_mode:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)


@hooks.on_load_config
def instantiate_database(db_type: DBType, db_name: str, db_connection_string: str):
    global _database
    if db_type == "in-memory":
        _database = InMemoryDatabase()
    elif db_type == "mongo":
        _database = VirtoolMongoDB(db_name, db_connection_string)
    elif db_type == "proxy":
        raise NotImplementedError("Proxy database is not yet supported.")
    else:
        raise ValueError(f"{db_type} is not a supported database type.")


@hooks.on_load_config
def add_database_fixture(direct_db_access_allowed: bool, scope: FixtureScope):
    global _database
    if direct_db_access_allowed:
        scope["database"] = _database


@hooks.on_load_config
def instantiate_environment(is_analysis_workflow: bool, job: Job):
    global _environment
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

        if "subtraction_id" in job.args:
            if isinstance(job.args["subtraction_id"], str):
                _environment.data_providers.subtraction_providers = \
                    [SubtractionDataProvider(job.args["subtraction_id"], _database.subtractions)]
            else:
                _environment.data_providers.subtraction_providers = \
                    [SubtractionDataProvider(id_, _database.subtractions) for id_ in job.args["subtraction_id"]]
    else:
        _environment = WorkflowEnvironment(job)


def start():
    ...
