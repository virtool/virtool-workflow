from virtool_workflow import runtime, hooks, data_model
from virtool_workflow.config.configuration import load_config


@hooks.use_job
def make_mock_job():
    return data_model.Job("test_job", {})


async def test_start():
    await load_config(dev_mode=True, is_analysis_workflow=True)
    await runtime.start()
