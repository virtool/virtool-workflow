from typing import Callable, Any, Optional
from inspect import signature, iscoroutinefunction, isgeneratorfunction
from functools import wraps
from abc import abstractmethod, ABC
from itertools import chain
from contextlib import AbstractContextManager

from .workflow import Workflow


class InvalidWorkflowFixtureError(ValueError):
    pass


class WorkflowFixture(Callable, ABC):

    @staticmethod
    @abstractmethod
    def fixture_func(*args, **kwargs):
        pass

    def __call__(self, *args, **kwargs):
        return self.fixture_func(*args, **kwargs)

    @staticmethod
    def types():
        return {cls.__name__: cls for cls in WorkflowFixture.__subclasses__()}


class WorkflowFixtureScope(AbstractContextManager):

    def __init__(self):
        self._instances = {}
        self._generators = []

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self._instances = {}
        for gen in self._generators:
            none = next(gen, None)
            if none is not None:
                raise InvalidWorkflowFixtureError("Fixture must only yield once")
        self._generators = []

    def instantiate(self, fixture: WorkflowFixture):
        injected = self.inject(fixture.__class__.fixture_func)

        if isgeneratorfunction(fixture.__class__.fixture_func):
            gen = injected()
            self._generators.append(gen)
            instance = next(gen)
        else:
            instance = injected()

        self._instances[fixture.__class__.__name__] = instance
        return instance

    def get_fixture(self, name: str):
        if name in self._instances:
            return self._instances[name]

        fixture_types = WorkflowFixture.types()
        if name in fixture_types:
            return self.instantiate(fixture_types[name]())

    def add_instance(self, instance: Any, *names: str):
        for name in names:
            self._instances[name] = instance

    def inject(self, func: Callable, **kwargs):
        sig = signature(func)
        fixture_types = WorkflowFixture.types()

        fixtures = {param: self.get_fixture(param)
                    for param in sig.parameters
                    if param in chain(fixture_types, self._instances)}

        fixtures.update(kwargs)

        if iscoroutinefunction(func):
            @wraps(func)
            async def injected(*args, **_kwargs):
                _kwargs.update(fixtures)
                return await func(*args, **_kwargs)
        else:
            @wraps(func)
            def injected(*args, **_kwargs):
                _kwargs.update(fixtures)
                return func(*args, **_kwargs)

        return injected

    def inject_workflow(self, workflow: Workflow):
        workflow.on_startup = [self.inject(f) for f in workflow.on_startup]
        workflow.on_cleanup = [self.inject(f) for f in workflow.on_cleanup]
        workflow.steps = [self.inject(f) for f in workflow.steps]


def workflow_fixture(func: Callable, name: Optional[str] = None):
    class _Fixture(WorkflowFixture):
        fixture_func = func

    _Fixture.__name__ = _Fixture.__qualname__ = name if name else func.__name__
    return _Fixture()
