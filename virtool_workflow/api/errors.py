from contextlib import asynccontextmanager

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
                                        on_409=AlreadyFinalized,
                                        on_404=NotFound,
                                        on_403=InsufficientJobRights,
                                        on_other=JobsAPIServerError):
    try:
        response_json = await response.json()
    except ContentTypeError:
        response_json = {}

    if 200 <= response.status < 300:
        yield response_json
    else:
        try:
            response_json = await response.json()
            response_message = response_json["message"]
        except ContentTypeError:
            response_message = await response.text()
        except KeyError:
            response_message = response_json

        if response.status == 404:
            raise on_404(response_message)
        elif response.status == 409:
            raise on_409(response_message)
        elif response.status == 403:
            raise on_403(response_message)
        else:
            raise on_other(response_message)
