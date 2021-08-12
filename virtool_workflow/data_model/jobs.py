from dataclasses import dataclass, field
from typing import List, Literal


State = Literal["complete", "cancelled", "error", "running"]


@dataclass(frozen=True)
class Status:
    """The status of a Virtool Job."""
    error: State
    progress: float
    stage: str
    state: str
    timestamp: str


@dataclass
class Job:
    """A Virtool Job."""
    id: str
    """Unique ID for the job."""
    args: dict
    """Workflow specific arguments."""
    mem: int = 8
    """The maximum amount of memory used in GB."""
    proc: int = 4
    """The number of processes used."""
    status: List[Status] = field(default_factory=lambda: [])
    """The status log for the job."""
    workflow: str = None
    """The name of the workflow which should be used."""
    key: str = None
    """The auth key for the jobs API."""
