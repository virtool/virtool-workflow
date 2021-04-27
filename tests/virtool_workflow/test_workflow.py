from virtool_workflow import hooks


async def test_correct_progress(test_workflow, runtime):
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

    results = await runtime.execute(test_workflow)

    for result, progress in zip(results, range(1, 11)):
        assert int(result) == progress


async def test_on_update_called(test_workflow, runtime):
    calls = 0

    @hooks.on_update
    async def _on_update():
        nonlocal calls
        calls += 1

    await runtime.execute(test_workflow)

    assert calls == 4
