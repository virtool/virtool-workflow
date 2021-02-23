import aiohttp

from virtool_workflow.fixtures.scoping import api_scope


@api_scope.fixture
async def http_client():
    async with aiohttp.ClientSession() as session:
        yield session
