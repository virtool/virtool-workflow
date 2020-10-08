from typing import Callable
from inspect import signature, iscoroutinefunction
from functools import wraps


class WorkflowFixture(Callable):
    _instances = {}

    def __init_subclass__(cls, fixture_func: Callable, *args, **kwargs):
        super(WorkflowFixture, cls).__init_subclass__(*args, **kwargs)
        cls.fixture_func = fixture_func

    def __init__(self):
        self.injected = self.inject(self.__class__.fixture_func)

    def __call__(self, *args, **kwargs):
        return self.fixture_func(*args, **kwargs)

    def instantiate(self, *args, **kwargs):
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

        print(fixtures)

        if not iscoroutinefunction(func):
            @wraps(func)
            def injected(*args, **_kwargs):
                _kwargs.update(fixtures)
                return func(*args, **_kwargs)
        else:
            @wraps(func)
            async def injected(*args, **_kwargs):
                _kwargs.update(fixtures)
                return await func(*args, **_kwargs)

        return injected


def workflow_fixture(func: Callable):
    class _Fixture(WorkflowFixture, fixture_func=func):
        pass

    _Fixture.__name__ = _Fixture.__qualname__ = func.__name__
    return _Fixture
