import asyncio

from virtool_workflow import step


@step
async def waste_time():
    for _ in range(10):
        await asyncio.sleep(1)
