from virtool_workflow import runtime, hooks, data_model


@hooks.use_job
def make_mock_job():
    return data_model.Job("test_job", {})


async def test_start():
    await runtime.start()
