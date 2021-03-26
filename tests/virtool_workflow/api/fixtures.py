import aiohttp
import pytest
from aiohttp import web

from tests.virtool_workflow.api.mocks.mock_api import mock_routes


@pytest.fixture
def loop(event_loop):
    return event_loop


@pytest.fixture
async def jobs_api_url():
    return "/api"


@pytest.fixture
async def aiohttp_app(loop):
    app = web.Application(loop=loop)

    for route_table in mock_routes:
        app.add_routes(route_table)

    return app


@pytest.fixture
async def http_no_decompress(aiohttp_client, aiohttp_app):
    return await aiohttp_client(aiohttp_app, auto_decompress=False)


@pytest.fixture
async def http_no_decompress(aiohttp_app, aiohttp_client) -> aiohttp.ClientSession:
    return await aiohttp_client(aiohttp_app, auto_decompress=True)
