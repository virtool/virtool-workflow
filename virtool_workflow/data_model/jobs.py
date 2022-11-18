from typing import Optional

from virtool_core.models.job import Job


class WFJob(Job):
    """
    A Virtool Job.

    Inherits from the core Job model, but includes the workflow authentication key.
    """

    key: Optional[str] = None
