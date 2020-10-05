from virtool_workflow import execute


async def test_execute(test_workflow):
    result = await execute.execute(test_workflow)
    assert result["start"]
    assert result["1"]
    assert result["2"]
    assert result["clean"]
    

async def test_respond_errors(test_workflow):

    @test_workflow.step
    async def throw_error(wf, ctx):
        raise Exception()

    async def raise_exception(error: execute.WorkflowError):
        assert error.context.current_step == 3
        return "Step 3 skipped due to internal error"

    updates = []
    
    async def receive_updates(ctx, update):
        updates.append(update)

    await execute.execute(test_workflow, on_error=raise_exception, on_update=receive_updates)
    assert "Step 3 skipped due to internal error" in updates


async def test_correct_traceback_data(test_workflow):

    arg1, arg2 = "arg1", "arg2"
    
    @test_workflow.step
    async def raise_exception(_, __):
        raise ValueError(arg1, arg2)

    def assert_correct_traceback(error):
        tb = error.traceback_data
        assert tb["type"] == "ValueError"
        assert arg1, arg2 in tb["details"]

    try:
        await execute.execute(test_workflow)
    except execute.WorkflowError as error:
        assert_correct_traceback(error)

    async def on_error(error):
        assert_correct_traceback(error)
        on_error.called = True

    await execute.execute(test_workflow, on_error=on_error)

    assert on_error.called


async def test_correct_progress(test_workflow):

    async def check_progress(wf, ctx):
        wf.results[str(ctx.current_step)] = (float(ctx.current_step) / float(len(wf.steps)))
        assert ctx.progress == wf.results[str(ctx.current_step)]

    test_workflow.steps = [check_progress] * 10
    test_workflow.on_startup = []
    test_workflow.on_cleanup = []

    results = await execute.execute(test_workflow)

    for result, progress in zip(results, range(1, 11)):
        assert int(result) == progress


async def test_on_update_called(test_workflow):

    async def on_update(ctx, update):
        on_update.calls += 1

    async def on_state_change(ctx):
        on_state_change.calls += 1

    on_update.calls = 0
    on_state_change.calls = 0

    await execute.execute(test_workflow, on_update=on_update, on_state_change=on_state_change)

    assert on_update.calls == 4
    assert on_state_change.calls == 4



