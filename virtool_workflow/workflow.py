from inspect import signature, iscoroutinefunction
from functools import wraps
from typing import Callable, Sequence, Optional, Awaitable, Iterable, Any, Dict
from .context import WorkflowExecutionContext

WorkflowStep = Callable[["Workflow", WorkflowExecutionContext], Awaitable[Optional[str]]]
"""Async function representing a step in a Virtool Workflow."""


def _coerce_signature_to_workflow_step(func: Callable):
    """
    Coerce the signature of a function to the signature of WorkflowStep

    :param func: The function to coerce
    :return: An equivalent async function with the signature of WorkflowStep
    """

    sig = signature(func)
    n_params = len(sig.parameters)

    if not iscoroutinefunction(func):
        func_ = func

        @wraps(func_)
        async def async_func(*args, **kwargs):
            return func_(*args, **kwargs)

        func = async_func

    if n_params == 1:
        @wraps(func)
        async def _func(_, context):
            return await func(context)
    elif n_params == 0:
        @wraps(func)
        async def _func(_, __):
            return await func()
    else:
        _func = func

    return _func


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
    results: Dict[str, Any]

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
        obj.results = {}
        if startup:
            obj.on_startup.extend(startup)
        if cleanup:
            obj.on_cleanup.extend(cleanup)
        if steps:
            obj.steps.extend(steps)
        return obj

    def startup(self, action: Callable):
        """Decorator for adding a step to workflow startup."""
        step = _coerce_signature_to_workflow_step(action)
        self.on_startup.append(step)
        return action

    def cleanup(self, action: Callable):
        """Decorator for adding a step to workflow cleanup."""
        step = _coerce_signature_to_workflow_step(action)
        self.on_cleanup.append(step)
        return action

    def step(self, step: Callable):
        """Decorator for adding a step to the workflow."""
        step_ = _coerce_signature_to_workflow_step(step)
        self.steps.append(step_)
        return step
