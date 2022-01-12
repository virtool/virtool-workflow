"""Main definitions for Virtool Workflows."""
from typing import Callable, Iterable, Optional, Sequence
from virtool_workflow.utils import coerce_to_coroutine_function

from fixtures import FixtureScope
from virtool_workflow._steps import WorkflowStep


class Workflow:
    """
    A Workflow is a step-wise, long-running operation.

    A workflow is comprised of:
        1. a set of functions to be executed on startup (.on_startup)
        2. a set of step functions which will be executed in order (.steps)
        3. a set of functions to be executed once all steps are completed (.on_cleanup)
    """

    on_startup: Sequence[WorkflowStep]
    on_cleanup: Sequence[WorkflowStep]
    steps: Sequence[WorkflowStep]

    def __new__(
        cls,
        *args,
        startup: Optional[Iterable[WorkflowStep]] = None,
        cleanup: Optional[Iterable[WorkflowStep]] = None,
        steps: Optional[Iterable[WorkflowStep]] = None,
        **kwargs
    ):
        """
        :param startup: An initial set of startup steps.
        :param cleanup: An initial set of cleanup steps.
        :param steps: An initial set of steps.
        """
        obj = super().__new__(cls)
        obj.on_startup = []
        obj.on_cleanup = []
        obj.steps = []
        if startup:
            obj.on_startup.extend(startup)
        if cleanup:
            obj.on_cleanup.extend(cleanup)
        if steps:
            obj.steps.extend(steps)
        return obj

    def startup(self, action: Callable) -> Callable:
        """Decorator for adding a step to workflow startup."""
        action = WorkflowStep.from_callable(action)
        self.on_startup.append(action)
        return action

    def cleanup(self, action: Callable) -> Callable:
        """Decorator for adding a step to workflow cleanup."""
        action = WorkflowStep.from_callable(action)
        self.on_cleanup.append(action)
        return action

    def step(self, step: Callable) -> Callable:
        """Decorator for adding a step to the workflow."""
        step = WorkflowStep.from_callable(step)
        self.steps.append(step)
        return step
