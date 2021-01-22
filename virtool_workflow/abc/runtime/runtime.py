from abc import ABC, abstractmethod
from typing import Dict, Any, Callable, Awaitable, List

from virtool_workflow import Workflow, FixtureScope, WorkflowExecution
from virtool_workflow.data_model import Job, Index, Analysis, Sample, Reference, Subtraction, HMM


class AbstractRuntime(ABC, FixtureScope):

    def __init__(
            self,
            job: Job,
            analysis: Analysis = None,
            sample: Sample = None,
            reference: Reference = None,
            indexes: List[Index] = None,
            subtractions: List[Subtraction] = None,
            hmms: HMM = None,
    ):
        self["job"] = job

        if analysis:
            self["analysis"] = analysis
        if sample:
            self["sample"] = sample
        if reference:
            self["reference"] = reference
        if indexes:
            self["indexes"] = indexes
        if subtractions:
            self["subtractions"] = subtractions
        if hmms:
            self["hmms"] = hmms

    async def execute(self, workflow: Workflow) -> Dict[str, Any]:
        """Execute a Workflow."""
        return await WorkflowExecution(workflow, self)

    async def execute_function(self, func: Callable[..., Awaitable[Any]]) -> Any:
        """Execute a function in the runtime context."""
        return await (await self.bind(func))

