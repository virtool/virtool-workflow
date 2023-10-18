import asyncio

import pytest


@pytest.fixture()
async def loop(event_loop):
    """
    Ensure the correct event loop is used.

    pytest-asyncio alters the asyncio event loop policy which can lead
    to :func:`asyncio.get_event_loop()` returning a different event loop
    than an async test will run in. Using this fixture will ensure that
    the same event loop is used by the test and any async fixtures requested.

    The relevant issue can be found at:

    https://github.com/pytest-dev/pytest-asyncio/issues/154
    """
    return asyncio.get_event_loop()
