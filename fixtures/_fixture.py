import inspect
from functools import wraps
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any, Dict, NewType, Protocol, runtime_checkable

FixtureValue = NewType('FixtureValue', Any)
"""A return value from a :class:`Fixture` callable."""


@runtime_checkable
class Fixture(Protocol):
    """
    A Protocol formally defining any attributes which are
    added to a fixture function via @:func:`fixture`.

    Enables `isinstance(function, Fixture)` checks to be made.

    """
    __name__: str
    __return_protocol__: Protocol
    __hide_params__: bool
    __follow_wrapped__: bool

    async def __call__(self, *args, **kwargs) -> FixtureValue:
        raise NotImplementedError()


_fixtures = ContextVar("fixtures")


def get_fixtures() -> Dict[str, Fixture]:
    """
    get the fixtures dictionary for the current context.

    If it does not exist, a new dictionary is created.
    """
    try:
        return _fixtures.get()
    except LookupError:
        _fixtures.set({})
        return _fixtures.get()


@contextmanager
def fixture_context(*fixtures: Fixture, copy_context=True) -> Dict[str, Fixture]:
    """
    Enter a new fixture context.

    Any fixtures created within the `with` block will not be available outside of it.

    :param fixtures: Any fixtures which should be included in the context.
                     If a fixture with the same name is already present, the
                     new fixture will be used instead.
    :param copy_context: Copy the fixtures dict from the current context, defaults to True.


    :yield: A dictionary mapping fixture names to :class:`Fixture` functions.
    """
    if copy_context is True:
        current_fixtures = get_fixtures()
        _fixtures_copy = current_fixtures.copy()
    else:
        _fixtures_copy = {}

    for fixture in fixtures:
        _fixtures_copy[fixture.__name__] = fixture

    token = _fixtures.set(_fixtures_copy)

    try:
        yield _fixtures.get()
    finally:
        _fixtures.reset(token)


def runs_in_new_fixture_context(*fixtures, copy_context=True):
    """Decorator which causes the function to be executed in a new fixture context."""
    def _deco(function: callable):
        if inspect.iscoroutinefunction(function):
            @wraps(function)
            async def _in_new_context(*args, **kwargs):
                with fixture_context(*fixtures, copy_context=copy_context):
                    return await function(*args, **kwargs)
        else:
            @wraps(function)
            def _in_new_context(*args, **kwargs):
                with fixture_context(*fixtures, copy_context=copy_context):
                    return function(*args, **kwargs)

        return _in_new_context
    return _deco


def fixture(
    function: callable = None,
    protocol: Protocol = None,
    hide_params: bool = True,
):
    """
    Create a new fixture.

    :param func: The fixture function
    :param protocol: An optional return protocol for the fixture, used when
                        rendering documentation for a fixture which returns a function.
    :param hide_params: Hide the arguments to the fixture when the documentation
                        is rendered, defaults to True
    :return: A fixture function, if :obj:`func` was given, or a decorator to create one.
    """
    if function is None:
        return lambda _func: fixture(_func, protocol, hide_params)

    if function.__name__.startswith("_"):
        function.__name__ = function.__name__.lstrip("_")

    function.__return_protocol__ = protocol
    function.__hide_params__ = hide_params
    function.__follow_wrapped__ = True

    fixtures = get_fixtures()
    fixtures[function.__name__] = function

    return function
