from dataclasses import dataclass
from typing import List
from datetime import datetime


@dataclass(frozen=True)
class Status:
    error: str
    progress: float
    stage: str
    state: str
    timestamp: datetime


@dataclass(frozen=True)
class User:
    id: str


@dataclass(frozen=True)
class Job:
    _id: str
    """Unique ID for the job."""
    args: dict
    """Workflow specific arguments."""
    mem: int
    """The maximum amount of memory used in GB."""
    proc: int
    """The number of processes used."""
    status: List[Status]
    """The status log for the job."""
    task: str
    """The name of the workflow which should be used."""
    user: User
    """Information about the user which requested the job."""


