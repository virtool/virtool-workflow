from virtool_workflow_runtime import runtime
from virtool_workflow_runtime.db import VirtoolDatabase
from virtool_workflow_runtime.config.configuration import db_name, db_connection_string
from virtool_workflow.fixtures.workflow_fixture import workflow_fixtures
from virtool_workflow.db.utils import convert_job_to_job_document
from virtool_workflow.data_model import Job


async def test_execute(test_workflow):
    db = VirtoolDatabase(db_name(), db_connection_string())

    await db["jobs"].insert_one(convert_job_to_job_document(Job("1", {})))

    await runtime.execute(test_workflow, runtime.DirectDatabaseAccessRuntime("1"))


async def test_fixtures_loaded(test_workflow):
    with runtime.runtime_scope:
        types = set(runtime.runtime_scope.available)
        expected_fixtures = {'state',
                             'proc',
                             'mem',
                             'redis_connection_string',
                             'redis_job_list_name',
                             'no_sentry',
                             'dev_mode',
                             'db_name',
                             'db_connection_string',
                             'thread_pool_executor',
                             'run_in_executor',
                             'run_subprocess',
                             'data_path',
                             'work_path',
                             'cache_path',
                             'subtraction_data_path',
                             'subtraction_path',
                             'subtractions',
                             'analysis_path',
                             'sample_path',
                             'index_path',
                             'raw_path',
                             'temp_cache_path',
                             'paired',
                             'library_type',
                             'sample',
                             'parsed_fastqc',
                             'unprepared_reads',
                             'reads'}

        assert expected_fixtures <= types

