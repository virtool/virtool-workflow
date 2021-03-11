from typing import Protocol

from virtool_workflow.data_model import Job, Status


class JobProviderProtocol(Protocol):
    async def __call__(self, id_: str) -> Job:
        """Fetch a job with the given id."""
        ...


class PushStatus(Protocol):
    async def __call__(self, status: Status):
        """Update the status of a job."""
        ...
