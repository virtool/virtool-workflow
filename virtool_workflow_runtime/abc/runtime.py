from abc import ABC, abstractmethod
from typing import Dict, Any, Callable, Awaitable

from virtool_workflow import Workflow, WorkflowExecution, WorkflowFixtureScope


class AbstractRuntime(ABC):

    @abstractmethod
    async def execute(self, workflow: Workflow) -> Dict[str, Any]:
        """Execute a Workflow."""
        ...

    @abstractmethod
    async def execute_function(self, func: Callable[..., Awaitable[Any]]) -> Any:
        """Execute a function in the runtime context."""
        ...

    @property
    @abstractmethod
    def scope(self) -> WorkflowFixtureScope:
        """The initialized `WorkflowFixtureScope`"""
        ...

    @property
    @abstractmethod
    def execution(self) -> WorkflowExecution:
        ...

    @execution.setter
    @abstractmethod
    def execution(self, _executor: WorkflowExecution):
        ...
