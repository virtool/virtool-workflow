from contextlib import asynccontextmanager
from typing import Dict, Type

from aiohttp import ContentTypeError


class JobAlreadyAcquired(Exception):
    def __init__(self, job_id: str):
        super(JobAlreadyAcquired, self).__init__(f"Job {job_id} is has already been acquired.")


class JobsAPIServerError(Exception):
    ...


class InsufficientJobRights(Exception):
    ...


class NotFound(KeyError):
    ...


class AlreadyFinalized(Exception):
    ...


@asynccontextmanager
async def raising_errors_by_status_code(response,
                                        status_codes_to_exceptions: Dict[int, Type[Exception]] = None):
    """
    Raise exceptions based on the result status code.

    If the status code is between 200 and 299 then this context manager will have no effect, other than
    getting the JSON body of the response.

    :param response: The aiohttp response object.
    :param status_codes_to_exceptions: A dict associating status codes to exceptions that should be raised.
    :return: The response json as a dict, if it is available.
    """
    if status_codes_to_exceptions is None:
        status_codes_to_exceptions = {
            404: NotFound,
            409: AlreadyFinalized,
            403: InsufficientJobRights,
            500: JobsAPIServerError,
        }

    response_json = None

    try:
        response_json = await response.json()
        response_message = response_json["message"]
    except ContentTypeError:
        response_message = await response.text()
    except (KeyError, TypeError):
        response_message = str(response_json)

    if response.status in status_codes_to_exceptions:
        raise status_codes_to_exceptions[response.status](response_message)
    else:
        yield response_json
