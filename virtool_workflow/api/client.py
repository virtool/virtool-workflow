import aiohttp


async def http_client():
    async with aiohttp.ClientSession() as session:
        yield session
