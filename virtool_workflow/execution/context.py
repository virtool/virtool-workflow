"""Execution context for Virtool Workflows."""
from enum import Enum
from typing import Optional

from virtool_workflow.execution.hooks import hook

State = Enum("State", "WAITING STARTUP RUNNING CLEANUP FINISHED")



class WorkflowExecutionContext:
    """
    Execution context for a workflow.Workflow.

    Contains the current execution state and manages updates.
    """

    def __init__(self):
        self.on_state_change = hook(_on_state_change)
        self.on_update = hook(_on_update)

        self._updates = []

        self._state = State.WAITING

        self.current_step = 0
        self.progress = 0.0
        self.error = None

    async def send_update(self, *update: Optional[str]):
        """
        Send an update.

        All functions registered by :func:`on_update` will be called.

        :param update: A string update to send.
        """
        for update_ in update:
            if update:
                self._updates.append(update_)
                await self.on_update.trigger(self, update_)
    @property
    def state(self) -> State:
        """The current :class:`State` of the executing workflow."""
        return self._state

    async def set_state(self, new_state: State):
        """Change the state of the executing workflow."""
        await self.on_state_change.trigger(self._state, new_state)
        self._state = new_state
