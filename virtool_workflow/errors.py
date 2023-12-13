from subprocess import SubprocessError


class IllegalJobArguments(ValueError):
    """The `job.args` dict is in an illegal state."""

    ...


class InsufficientJobRights(Exception):
    ...


class JobAlreadyAcquired(Exception):
    def __init__(self, job_id: str):
        super(JobAlreadyAcquired, self).__init__(
            f"Job {job_id} is has already been acquired."
        )


class JobAlreadyFinalized(Exception):
    ...


class JobsAPIError(Exception):
    """A base exception for errors due to HTTP errors from the jobs API."""

    ...


class JobsAPIBadRequest(JobsAPIError):
    """A ``400 Bad Request`` response from the jobs API."""

    status = 400
    ...


class JobsAPIForbidden(JobsAPIError):
    status = 403
    ...


class JobsAPINotFound(JobsAPIError):
    status = 404
    ...


class JobsAPIConflict(JobsAPIError):
    status = 409
    ...


class JobsAPIServerError(JobsAPIError):
    status = 500
    ...


class MissingJobArgument(ValueError):
    """The `job.args` dict is missing a required key for some funcionality."""

    ...


class NotFound(KeyError):
    ...


class SubprocessFailed(SubprocessError):
    """Subprocess exited with non-zero status during a workflow."""
