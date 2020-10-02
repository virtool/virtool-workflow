import asyncio
from enum import Enum, auto
from typing import Callable, Optional, Awaitable

class State(Enum):
    WAITING = auto()
    STARTUP = auto()
    RUNNING = auto()
    CLEANUP = auto()
    FINISHED = auto()


UpdateListener = Callable[["WorkflowExecutionContext", Optional[str]], Awaitable[None]]
StateListener = Callable[["WorkflowExecutionContext"], Awaitable[None]]


class WorkflowExecutionContext:
    """Execution context for a workflow.Workflow.

    Contains the current execution state and manages updates
    """

    def __init__(
            self,
            on_update: Optional[UpdateListener] = None,
            on_state_change: Optional[StateListener] = None,
            event_loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    ):
        """
        :param on_update: Async callback function for workflow updates
        :param on_state_change: Async callback function for changes in WorkflowState
        """
        self.__updates = []
        self.__on_update = [] if not on_update else [on_update]
        self.__state = State.WAITING
        self.__on_state_change = [] if not on_state_change else [on_state_change]

        self.current_step = 0
        self.progress = 0.0
        self.error = None

        self._loop = event_loop

    def on_state_change(self, action: Callable[["WorkflowExecutionContext", str], Awaitable[None]]):
        """
        register a callback function to receive updates about the Workflow state

        :param action: async function to call when the WorkflowState changes. The current WorkflowExecutionContext
            is included as a parameter
        """
        self.__on_state_change.append(action)

    def on_update(self, action: Callable[["WorkflowExecutionContext", str], Awaitable[None]]):
        """
        register a callback function to receive updates sent from the worflow via :func:`send_update`

        :param action: async function to call when updates are received. The WorkflowExecutionContext and update string are
            included as parameters
        """
        self.__on_update.append(action)

    async def send_update(self, update: Optional[str]):
        for on_update in self.__on_update:
            await on_update(self, update)

    @property
    def state(self) -> State:
        return self.__state

    async def set_state(self, new_state: State):
        self.__state = new_state
        for on_state in self.__on_state_change:
            await on_state(self)
