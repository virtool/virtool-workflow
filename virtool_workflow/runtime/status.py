"""Utility functions for sending status updates."""
from virtool_workflow.api.jobs import push_status as _


async def send_status(push_status):
    await push_status(state="running")


async def send_complete(push_status, error):
    await push_status(state="complete", stage="completed")


async def send_failed(push_status, error, max_tb=50):
    await push_status(
        stage="",
        state="error",
        error=error,
        max_tb=max_tb,
    )


async def send_cancelled(push_status):
    await push_status(state="cancelled")
