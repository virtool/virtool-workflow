"""Execution context for Virtool Workflows."""
from enum import Enum, auto
from typing import Callable, Optional, Coroutine, Any


class State(Enum):
    """Enum for workflow execution states."""
    WAITING = auto()
    STARTUP = auto()
    RUNNING = auto()
    CLEANUP = auto()
    FINISHED = auto()


UpdateListener = Callable[["WorkflowExecutionContext", Optional[str]], Coroutine[Any, Any, None]]
StateListener = Callable[["WorkflowExecutionContext"], Coroutine[Any, Any, None]]


class WorkflowExecutionContext:
    """
    Execution context for a workflow.Workflow.

    Contains the current execution state and manages updates.
    """

    def __init__(self):
        """
        """
        self._updates = []


        self._state = State.WAITING

        self.current_step = 0
        self.progress = 0.0
        self.error = None

    async def send_update(self, update: Optional[str]):
        """
        Send an update.

        All functions registered by :func:`on_update` will be called.

        :param update: A string update to send.
        """
        self.scope["update"] = update
        self.on_update.__trigger__()

    @property
    def state(self) -> State:
        """The current :class:`State` of the executing workflow."""
        return self._state

    async def set_state(self, new_state: State):
        """Change the state of the executing workflow."""
        self._state = new_state
        for on_state in self._on_state_change:
            await on_state(self)
