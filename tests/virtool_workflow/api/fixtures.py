import aiohttp
import pytest
from aiohttp import web

from tests.virtool_workflow.api.mock_api import mock_routes


@pytest.fixture
def loop(event_loop):
    return event_loop


@pytest.fixture
async def jobs_api_url():
    return "/api"


@pytest.fixture
async def http(loop, aiohttp_client) -> aiohttp.ClientSession:
    app = web.Application(loop=loop)

    app.add_routes(mock_routes)

    return await aiohttp_client(app)
