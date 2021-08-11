"""Utility functions for sending status updates."""


async def send_status(push_status, workflow, execution):
    await push_status(
        state="running",
        stage=workflow.steps[execution.current_step],
        progress=execution.progress,
    )


async def send_complete(push_status, workflow, execution):
    await push_status(
        state="complete",
        stage=workflow.steps[execution.current_step],
        progress=100,
    )


async def send_failed(push_status, error, workflow, execution):
    await push_status(
        state="error",
        stage=workflow.steps[execution.current_step],
        progress=100,
        error=str(error)
    )


async def send_cancelled(push_status, workflow, execution):
    await push_status(
        state="cancelled",
        stage=workflow.steps[execution.current_step],
        progress=execution.progress,
    )
