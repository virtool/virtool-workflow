from typing import Callable
from inspect import signature, iscoroutinefunction, isgeneratorfunction
from functools import wraps


class InvalidWorkflowFixtureError(ValueError):
    pass


class WorkflowFixture(Callable):
    _instances = {}
    _generators = []

    def __init_subclass__(cls, fixture_func: Callable, *args, **kwargs):
        super(WorkflowFixture, cls).__init_subclass__(*args, **kwargs)
        cls.fixture_func = fixture_func

    def __init__(self):
        self.injected = self.inject(self.__class__.fixture_func)

    def __call__(self, *args, **kwargs):
        return self.fixture_func(*args, **kwargs)

    # noinspection PyTypeChecker
    def instantiate(self, *args, **kwargs):
        if isgeneratorfunction(self.__class__.fixture_func):
            gen = self.injected(*args, **kwargs)
            fixture_ = next(gen)
            self._generators.append(gen)
        else:
            fixture_ = self.injected(*args, **kwargs)
        WorkflowFixture._instances[self.__class__.__name__] = fixture_
        return fixture_

    @staticmethod
    def types():
        return {cls.__name__: cls for cls in WorkflowFixture.__subclasses__()}

    @staticmethod
    def get_fixture(name: str):
        if name in WorkflowFixture._instances:
            return WorkflowFixture._instances[name]

        fixture_types = WorkflowFixture.types()
        if name in fixture_types:
            return fixture_types[name]().instantiate()

    @staticmethod
    def inject(func: Callable, **kwargs):
        sig = signature(func)
        fixture_types = WorkflowFixture.types()

        fixtures = {param: WorkflowFixture.get_fixture(param)
                    for param in sig.parameters
                    if param in fixture_types}

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

    @staticmethod
    def clean_instances():
        WorkflowFixture._instances = {}
        for gen in WorkflowFixture._generators:
            none = next(gen, None)
            if none is not None:
                raise InvalidWorkflowFixtureError("Fixture must only yield once")
        WorkflowFixture._generators = []



def workflow_fixture(func: Callable):
    class _Fixture(WorkflowFixture, fixture_func=func):
        pass

    _Fixture.__name__ = _Fixture.__qualname__ = func.__name__
    return _Fixture
