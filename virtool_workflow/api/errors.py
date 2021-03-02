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
