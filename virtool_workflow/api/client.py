from functools import wraps

import aiohttp
from pyfixtures import fixture


@fixture
async def http():
    """:class:`Aiohttp.ClientSession` instance to be used for workflows."""
    connector = aiohttp.TCPConnector(force_close=True, limit=100)

    async with aiohttp.ClientSession(
        auto_decompress=False, connector=connector
    ) as session:
        yield JobApiHttpSession(session)


@fixture
async def authenticated_http(job_id, key, http):
    """:class:`Aiohttp.ClientSession` instance which includes authentication headers for the jobs API."""
    http.auth = aiohttp.BasicAuth(login=f"job-{job_id}", password=key)
    return http


class JobApiHttpSession:
    """Wraps :class:`aiohttp.ClientSession` and adds authentication for the jobs API."""

    def __init__(self, client: aiohttp.ClientSession, auth: aiohttp.BasicAuth = None):
        self.client = client
        self.auth = auth

        self.delete = self._wrap_with_auth(self.client.delete)
        self.get = self._wrap_with_auth(self.client.get)
        self.patch = self._wrap_with_auth(self.client.patch)
        self.post = self._wrap_with_auth(self.client.post)
        self.put = self._wrap_with_auth(self.client.put)

    def _wrap_with_auth(self, method):
        @wraps(method)
        def _method_with_auth(*args, noauth=False, **kwargs):
            if "auth" not in kwargs and self.auth is not None and not noauth:
                kwargs["auth"] = self.auth

            return method(*args, **kwargs)

        return _method_with_auth
