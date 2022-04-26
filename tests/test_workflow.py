from virtool_workflow import hooks, WorkflowStep


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
        10: 1.0,
    }

    async def check_progress(progress, step_number):
        assert progress == correct_progress[step_number]

    test_workflow.steps = [WorkflowStep.from_callable(check_progress)] * 10
    test_workflow.on_startup = []
    test_workflow.on_cleanup = []

    results = await runtime.execute(test_workflow)

    for result, progress in zip(results, range(1, 11)):
        assert int(result) == progress
