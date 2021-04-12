import aiohttp


async def http():
    """:class:`Aiohttp.ClientSession` instance to be used for workflows."""
    async with aiohttp.ClientSession(auto_decompress=False) as session:
        yield session


async def authenticated_http(job_id, key, http):
    auth = aiohttp.BasicAuth(login=f"job-{job_id}", password=key)

    async with aiohttp.ClientSession(auto_decompress=False, auth=auth) as session:
        yield session
