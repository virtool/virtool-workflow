import asyncio
from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Callable, Sequence, Optional, MutableMapping, Awaitable, MutableSequence

class State(Enum):
    WAITING = auto()
    STARTUP = auto()
    RUNNING = auto()
    CLEANUP = auto()
    FINISHED = auto()


UpdateListener = Callable[["Context", str], Awaitable[None]]
StateListener = Callable[["Context"], Awaitable[None]]


class Context:

    """
    Execution context for a workflow.Workflow.
    Contains the current execution state and manages updates
    """

    def __init__(
            self, 
            on_update: Optional[UpdateListener] = None,
            on_state_change: Optional[StateListener] = None
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

    def on_state_change(self, action: Callable[["Context", str], Awaitable[None]]):
        """
        register a callback function to receive updates about the Workflow state

        :param action: async function to call when the WorkflowState changes. The current Context
            is included as a parameter
        """
        self.__on_state_change.append(action)

    def on_update(self, action: Callable[["Context", str], Awaitable[None]]):
        """
        register a callback function to receive updates sent from the worflow via :func:`send_update`

        :param action: async function to call when updates are received. The Context and update string are
            included as parameters
        """
        self.__on_update.append(action)

    async def send_update(self, update: str):
        for on_update in self.__on_update:
            await on_update(self, update)

    @property
    def state(self) -> State:
        return self.__state

    @state.setter
    def state(self, new_state: State):
        self.__state = new_state
        tasks = [asyncio.create_task(on_state(self)) for on_state in self.__on_state_change]
        asyncio.gather(*tasks)
