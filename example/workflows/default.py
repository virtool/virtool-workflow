import asyncio

from virtool_workflow import step


@step
async def step_1():
    await asyncio.sleep(1)


@step
async def step_2(step_number, results):
    await asyncio.sleep(3)
