from typing import Literal

State = Literal["waiting", "running", "complete", "cancelled", "error"]

CANCELLED = "cancelled"
COMPLETE = "complete"
ERROR = "error"
RUNNING = "running"
WAITING = "waiting"
