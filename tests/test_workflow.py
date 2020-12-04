from virtool_workflow.execution.execution import execute
from virtool_workflow import hooks, WorkflowError


async def test_execute(test_workflow):
    result = await execute(test_workflow)
    assert result["start"]
    assert result["1"]
    assert result["2"]
    assert result["clean"]
    

async def test_respond_errors(test_workflow):

    @test_workflow.step
    async def throw_error():
        raise Exception()

    @hooks.on_error(until=hooks.on_result)
    async def handle_error(error: WorkflowError):
        assert error.context.current_step == 3
        return "Step 3 skipped due to internal error"

    updates = []

    @hooks.on_update(until=hooks.on_workflow_finish)
    async def receive_updates(update):
        updates.append(update)

    await execute(test_workflow)
    assert "Step 3 skipped due to internal error" in updates


async def test_correct_traceback_data(test_workflow):
    arg1, arg2 = "arg1", "arg2"
    
    @test_workflow.step
    async def raise_exception():
        raise ValueError(arg1, arg2)

    def assert_correct_traceback(_error):
        tb = _error.traceback_data
        assert tb["type"] == "ValueError"
        assert arg1, arg2 in tb["details"]

    try:
        await execute(test_workflow)
    except WorkflowError as error:
        assert_correct_traceback(error)


async def test_correct_progress(test_workflow):

    correct_progress = {
        0: 0.0,
        1: 0.1,
        2: 0.2,
        3: 0.3,
        4: 0.4,
        5: 0.5,
        6: 0.6,
        7: 0.7,
        8: 0.8,
        9: 0.9,
        10: 1.0
    }

    async def check_progress(execution):
        assert execution.progress == correct_progress[execution.current_step]

    test_workflow.steps = [check_progress] * 10
    test_workflow.on_startup = []
    test_workflow.on_cleanup = []

    results = await execute(test_workflow)

    for result, progress in zip(results, range(1, 11)):
        assert int(result) == progress


async def test_on_update_called(test_workflow):

    calls = 0
    state_calls = 0

    @hooks.on_update
    async def _on_update():
        nonlocal calls
        calls += 1

    @hooks.on_state_change
    async def _on_state_change():
        nonlocal state_calls
        state_calls += 1

    _on_update.calls = 0
    _on_state_change.calls = 0

    await execute(test_workflow)

    assert calls == 4
    assert state_calls == 4

    hooks.on_update.callbacks.remove(_on_update)
    hooks.on_state_change.callbacks.remove(_on_state_change)

