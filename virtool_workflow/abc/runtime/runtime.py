from abc import ABC, abstractmethod
from typing import Dict, Any, Callable, Awaitable, List

from virtool_workflow import Workflow, WorkflowExecution, WorkflowFixtureScope
from virtool_workflow.data_model import Job, Index, Analysis, Sample, Reference, Subtraction


class AbstractRuntime(ABC):

    def __init__(
            self,
            job: Job,
            analysis: Analysis = None,
            sample: Sample = None,
            reference: Reference = None,
            indexes: List[Index] = None,
            subtractions: List[dict] = None,
    ):
        self.job = job
        self.analysis = analysis
        self.sample = sample
        self.indexes = indexes
        self.reference = reference
        self.subtractions = subtractions

        self.scope["job"] = job

        if analysis:
            self.scope["analysis"] = analysis
        if sample:
            self.scope["sample"] = sample
        if index:
            self.scope["index"] = index
        if reference:
            self.scope["reference"] = reference


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
