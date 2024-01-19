import asyncio
import functools

from aiohttp import (
    ClientConnectorError,
    ClientResponse,
    ContentTypeError,
    ServerDisconnectedError,
)
from structlog import get_logger

from virtool_workflow.errors import (
    JobsAPIBadRequest,
    JobsAPIConflict,
    JobsAPIForbidden,
    JobsAPINotFound,
    JobsAPIServerError,
)

logger = get_logger("api")


def retry(func):
    """Retry an API call five times when encountering the following exceptions:
      * ``ConnectionRefusedError``.
      * ``ClientConnectorError``.
      * ``ServerDisconnectedError``.

    These are probably due to transient issues in the cluster network.

    """

    @functools.wraps(func)
    async def wrapped(*args, **kwargs):
        attempts = 0

        try:
            return await func(*args, **kwargs)
        except (
            ConnectionRefusedError,
            ClientConnectorError,
            ServerDisconnectedError,
        ) as err:
            if attempts == 5:
                raise

            attempts += 1
            get_logger("runtime").info(
                f"Encountered {type(err).__name__}. Retrying in 5 seconds.",
            )
            await asyncio.sleep(5)

            return await func(*args, **kwargs)

    return wrapped


async def decode_json_response(resp: ClientResponse) -> dict | list | None:
    """Decode a JSON response from a :class:``ClientResponse``.

    Raise a :class:`ValueError` if the response is not JSON.

    :param resp: the response to decode
    :return: the decoded JSON
    """
    try:
        return await resp.json()
    except ContentTypeError:
        raise ValueError(f"Response from  {resp.url} was not JSON. {await resp.text()}")


async def raise_exception_by_status_code(resp: ClientResponse):
    """Raise an exception based on the status code of the response.

    :param resp: the response to check
    :raise JobsAPIBadRequest: the response status code is 400
    :raise JobsAPIForbidden: the response status code is 403
    :raise JobsAPINotFound: the response status code is 404
    :raise JobsAPIConflict: the response status code is 409
    :raise JobsAPIServerError: the response status code is 500
    """
    status_exception_map = {
        400: JobsAPIBadRequest,
        403: JobsAPIForbidden,
        404: JobsAPINotFound,
        409: JobsAPIConflict,
        500: JobsAPIServerError,
    }

    try:
        resp_json: dict | None = await resp.json()
    except ContentTypeError:
        resp_json = None

    if resp.status not in range(200, 299):
        if resp_json is None:
            try:
                message = await resp.text()
            except UnicodeDecodeError:
                message = "Could not decode response message"
        else:
            message = resp_json["message"] if "message" in resp_json else str(resp_json)

        if resp.status in status_exception_map:
            raise status_exception_map[resp.status](message)
        else:
            raise ValueError(
                f"Status code {resp.status} not handled for response\n {resp}",
            )
