import aiohttp


async def http():
    async with aiohttp.ClientSession() as session:
        yield session
