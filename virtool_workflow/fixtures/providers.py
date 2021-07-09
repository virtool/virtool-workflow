import logging
from typing import Protocol, Callable, Optional

logger = logging.getLogger(__name__)


class FixtureProvider(Protocol):
    """A callable which retrieves fixtures by name."""

    def __call__(self, name: str, request_from: Callable = None) -> Optional[Callable]:
        """
        Find a fixture within this group with the given param_name.

        :param name: The name of the requested fixture.
        :param request_from: The class of the fixture which is being instantiated. Set to None
            if the fixture is being bound to a function.
        :return: The fixture function with the given name, or None if it is not in this grouping
        """
        ...


def for_fixtures(*receivers: Callable, **fixtures):
    """
    Create a new fixture provider which only returns fixtures from :obj:`fixtures`
    if they are requested by particular fixtures.
    """

    def _grouping(param_name: str, request_from: Callable):
        if param_name in fixtures and (request_from in receivers):
            return fixtures[param_name]

    return _grouping


class FixtureGroup(FixtureProvider, dict):
    """A dict defining a group of fixture functions."""

    def __init__(self, *args, **kwargs):
        super(FixtureGroup, self).__init__()
        self.update(**{f.__name__: f for f in args})
        self.update(**kwargs)

    def __call__(self, name: str, _: Callable = None):
        if name in self:
            return self[name]

    def fixture(self, func: callable = None, protocol: Protocol = None, hide_params: bool = True):
        """
        Add a fixture to this :class`FixtureGroup`

        :param func: The fixture function
        :param protocol: An optional return protocol for the fixture, used when
                         rendering documentation for a fixture which returns a function.
        :param hide_params: Hide the arguments to the fixture when the documentation
                          is rendered, defaults to True
        :return: A fixture function, if :obj:`func` was given, or a decorator to create one.
        """
        if func is None:
            return lambda _func: self.fixture(_func, protocol, hide_params)

        if func.__name__.startswith("_"):
            func.__name__ = func.__name__.lstrip("_")
           
        self[func.__name__] = func

        func.is_workflow_fixture = True

        if protocol is not None:
            func.__return_protocol__ = protocol

        func.__hide_params__ = hide_params

        return func

    def fixtures(self):
        return self


class InstanceFixtureGroup(FixtureGroup):
    """A dict which acts as a :class:`FixtureProvider`, providing it's instances as fixture values."""

    def __call__(self, name: str, _: Callable = None):
        if name in self:
            return lambda: self[name]
