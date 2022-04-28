from asyncio import sleep

from virtool_workflow import Workflow, hooks


async def test_status_updates(db, create_job, exec_workflow, job_id):
    await create_job(args={})

    wf = Workflow()

    @wf.step
    def first(job):
        """Description of First."""
        assert job.status[-1]["state"] == "preparing"

    @wf.step
    def second(job):
        """Description of Second."""
        ...

    jobs = db.get_collection("jobs")
    steps_finished = 0

    @hooks.on_step_finish
    async def check_current_status(current_step):
        nonlocal steps_finished
        steps_finished += 1

        job = await jobs.find_one({"_id": job_id})
        status = job["status"][-1]

        if current_step is first:
            assert status["step_name"] == "First"
            assert status["step_description"] == "Description of First."
            assert status["state"] == "running"
        elif current_step is second:
            assert status["step_name"] == "Second"
            assert status["step_description"] == "Description of Second."
            assert status["state"] == "running"
        else:
            raise RuntimeError(f"Current step {current_step} is an illegal value")

    on_success_called = False

    @hooks.on_success(once=True)
    async def check_success_status():
        nonlocal on_success_called
        on_success_called = True

        # Wait for status to be received at virtool server
        await sleep(0.1)

        job = await jobs.find_one({"_id": job_id})
        status = job["status"][-1]

        assert status["state"] == "complete"

    await exec_workflow(wf)

    assert steps_finished == 2
    assert on_success_called is True


async def test_status_updates_with_error(db, create_job, exec_workflow, job_id):
    await create_job({})

    wf = Workflow()
    error = ValueError()

    @wf.step
    def raise_error():
        raise error

    error_hook_called = False

    @hooks.on_error(once=True)
    async def check_error_update_sent():
        nonlocal error_hook_called

        # Wait for status to be received at virtool server
        await sleep(0.1)

        job = await db.get_collection("jobs").find_one({"_id": job_id})

        status = job["status"][-1]

        assert status["state"] == "error"
        assert status["error"]["type"] == "ValueError"

        error_hook_called = True

    failure_hook_called = False

    @hooks.on_failure(once=True)
    async def check_failure_hook_called():
        nonlocal failure_hook_called
        failure_hook_called = True

    await exec_workflow(wf)

    assert error_hook_called is True
    assert failure_hook_called is True
