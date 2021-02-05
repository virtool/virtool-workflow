from typing import Protocol

from virtool_workflow.data_model import Job


class JobProvider(Protocol):
    def __call__(self, id_: str) -> Job:
        """Fetch a job with the given id."""
        ...
