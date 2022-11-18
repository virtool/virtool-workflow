"""Main definitions for Virtool Workflows."""
from dataclasses import dataclass, field
from typing import Callable, Sequence, Optional

from virtool_workflow.runtime.step import WorkflowStep


@dataclass
class Workflow:
    """
    A step-wise, long-running operation.
    """

    steps: Sequence[WorkflowStep] = field(default_factory=list)

    def step(self, step: Optional[Callable] = None, *, name: str = None) -> Callable:
        """Decorator for adding a step to the workflow."""
        if step is None:

            def _decorator(func: Callable):
                self.step(func, name=name)

            return _decorator

        step = WorkflowStep.from_callable(step, display_name=name)
        self.steps.append(step)
        return step
