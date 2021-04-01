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
async def mock_jobs_api_app(loop):
    app = web.Application(loop=loop)

    for route_table in mock_routes:
        app.add_routes(route_table)

    return app


@pytest.fixture
async def http(mock_jobs_api_app, aiohttp_client) -> aiohttp.ClientSession:
    """Create an http client for accessing the mocked Jobs API."""
    return await aiohttp_client(mock_jobs_api_app, auto_decompress=False)
