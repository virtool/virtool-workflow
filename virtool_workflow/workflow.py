import asyncio
from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Callable, Sequence, Optional, Awaitable, MutableSequence, Iterable, Any

WorkflowStep = Callable[["Workflow", Context], Awaitable[Optional[str]]]

class Workflow:
    """A Workflow is a step-wise, long-running operation.
    
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
        :param steps: An inital set of steps.
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

    def startup(self, action: WorkflowStep):
        """Decorator for adding a step to workflow startup"""
        self.on_startup.append(action)
        return action

    def cleanup(self, action: WorkflowStep):
        """Decorator for adding a step to workflow cleanup"""
        self.on_cleanup.append(action)
        return action

    def step(self, step: WorkflowStep):
        """Decorator for adding a step to the workflow"""
        self.steps.append(step)
        return step
