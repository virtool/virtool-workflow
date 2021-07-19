"""Main definitions for Virtool Workflows."""
from typing import Any, Callable, Coroutine, Iterable, Optional, Sequence
from virtool_workflow.utils import coerce_to_coroutine_function

from fixtures import FixtureScope

WorkflowStep = Callable[..., Coroutine[Any, Any, None]]


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
        self.on_startup.append(coerce_to_coroutine_function(action))
        return action

    def cleanup(self, action: Callable) -> Callable:
        """Decorator for adding a step to workflow cleanup."""
        self.on_cleanup.append(coerce_to_coroutine_function(action))
        return action

    def step(self, step: Callable) -> Callable:
        """Decorator for adding a step to the workflow."""
        self.steps.append(coerce_to_coroutine_function(step))
        return step

    def merge(self, *workflows: "Workflow"):
        """Merge steps from other workflows into this workflow."""
        self.steps.extend(step for w in workflows for step in w.steps)
        self.on_startup.extend(
            step for w in workflows for step in w.on_startup)
        self.on_cleanup.extend(
            step for w in workflows for step in w.on_cleanup)

        return self

    async def bind_to_fixtures(self, scope: FixtureScope):
        """
        Bind a workflow to fixtures.

        This is a convenience method for binding a workflow to a set of fixtures.
        """
        self.on_startup = [await scope.bind(f) for f in self.on_startup]
        self.on_cleanup = [await scope.bind(f) for f in self.on_cleanup]
        self.steps = [await scope.bind(f) for f in self.steps]

        return self
