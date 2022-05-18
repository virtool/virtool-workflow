"""Main definitions for Virtool Workflows."""
from dataclasses import dataclass, field
from typing import Callable, Sequence

from virtool_workflow._steps import WorkflowStep


@dataclass
class Workflow:
    """
    A step-wise, long-running operation.
    """

    steps: Sequence[WorkflowStep] = field(default_factory=list)

    def step(self, step: Callable) -> Callable:
        """Decorator for adding a step to the workflow."""
        step = WorkflowStep.from_callable(step)
        self.steps.append(step)
        return step
