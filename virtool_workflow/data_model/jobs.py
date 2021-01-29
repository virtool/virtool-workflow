from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class Status:
    """The status of a Virtool Job."""
    error: str
    progress: float
    stage: str
    state: str
    timestamp: str


@dataclass
class Job:
    """A Virtool Job."""
    _id: str
    """Unique ID for the job."""
    args: dict
    """Workflow specific arguments."""
    mem: int = 8
    """The maximum amount of memory used in GB."""
    proc: int = 4
    """The number of processes used."""
    status: List[Status] = field(default_factory=lambda: [])
    """The status log for the job."""
    task: str = None
    """The name of the workflow which should be used."""
