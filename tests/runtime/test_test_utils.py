from virtool_workflow_runtime.test_utils import runtime


async def test_runtime_fixture(runtime):

    def function_using_fixtures(data_path, work_path, dev_mode, run_subprocess, run_in_executor):
        return (
            data_path is not None,
            work_path is not None,
            dev_mode is not None,
            run_subprocess is not None,
            run_in_executor is not None,
        )

    results = await runtime.execute_function(function_using_fixtures)

    assert all(results)
