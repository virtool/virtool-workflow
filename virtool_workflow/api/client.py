import aiohttp


async def http():
    """:class:`Aiohttp.ClientSession` instance to be used for workflows."""
    async with aiohttp.ClientSession(auto_decompress=False) as session:
        yield session
