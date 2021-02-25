import aiohttp

from virtool_workflow.api.scope import api_scope


async def test_http_client():
    client = await api_scope.get_or_instantiate("http_client")

    assert isinstance(client, aiohttp.ClientSession)
   
    await api_scope.close()

    assert client.closed
