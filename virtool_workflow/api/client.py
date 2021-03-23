import aiohttp


async def http():
    async with aiohttp.ClientSession(auto_decompress=False) as session:
        yield session
