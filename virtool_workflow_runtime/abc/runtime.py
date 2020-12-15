from abc import ABC, abstractmethod
from virtool_workflow import Workflow, WorkflowExecution, WorkflowFixtureScope
from typing import Dict, Any, Callable, Awaitable


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
