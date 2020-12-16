from virtool_workflow import WorkflowFixture
from virtool_workflow_runtime import runtime
from virtool_workflow_runtime.db import VirtoolDatabase
from virtool_workflow_runtime.config.configuration import db_name, db_connection_string


async def test_execute(test_workflow):
    db = VirtoolDatabase(db_name(), db_connection_string())

    await db["jobs"].insert_one(dict(_id="1", args=dict()))

    await runtime.execute(test_workflow, runtime.DirectDatabaseAccessRuntime("1"))


async def test_fixtures_loaded(test_workflow):
    with runtime.runtime_scope:
        types = set(WorkflowFixture.types())
        expected_fixtures = {'state',
                             'database',
                             'temp_path_str',
                             'data_path_str',
                             'number_of_processes',
                             'memory_usage_limit',
                             'redis_connection_string',
                             'job_list_name',
                             'no_sentry',
                             'dev_mode',
                             'db_name',
                             'db_connection_string',
                             'thread_pool_executor',
                             'run_in_executor',
                             'run_subprocess',
                             'data_path',
                             'temp_path',
                             'cache_path',
                             'subtraction_data_path',
                             'subtraction_path',
                             'subtractions',
                             'analysis_path',
                             'sample_path',
                             'index_path',
                             'raw_path',
                             'temp_cache_path',
                             'temp_analysis_path',
                             'paired',
                             'library_type',
                             'sample',
                             'parsed_fastqc',
                             'unprepared_reads',
                             'reads'}

        assert expected_fixtures <= types

