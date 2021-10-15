"""Utility functions for sending status updates."""


async def send_status(push_status, workflow, execution):
    await push_status(state="running",)


async def send_complete(push_status, workflow, execution):
    await push_status(state="complete")


async def send_failed(push_status, error, workflow, execution):
    await push_status(
        state="error",
        error={"message": str(error)}
    )


async def send_cancelled(push_status, workflow, execution):
    await push_status(state="cancelled")
