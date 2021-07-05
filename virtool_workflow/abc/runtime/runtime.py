from abc import abstractmethod, ABC
from typing import Dict, Any

from virtool_workflow.workflow import Workflow


class AbstractWorkflowEnvironment(ABC):

    @abstractmethod
    async def execute(self, workflow: Workflow) -> Dict[str, Any]:
        """Execute a Workflow."""
        ...

    @abstractmethod
    async def execute_function(self, func: callable):
        """Execute a function in the runtime context."""
        ...
