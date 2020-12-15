from virtool_workflow_runtime.test_utils import runtime


async def test_runtime_fixture(runtime):

    def function_using_fixtures(data_path, temp_path, dev_mode, run_subprocess, run_in_executor):
        pass

    bound = await runtime.bind(function_using_fixtures)
    bound()
