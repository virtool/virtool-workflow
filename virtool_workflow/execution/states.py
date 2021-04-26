from typing import Literal

State = Literal["WAITING", "STARTUP", "RUNNING", "CLEANUP", "FINISHED"]

WAITING, STARTUP, RUNNING, CLEANUP, FINISHED = (
        "WAITING", "STARTUP", "RUNNING", "CLEANUP", "FINISHED"
        )
