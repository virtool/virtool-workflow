from typing import Protocol, Callable, Optional, Dict


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


def for_fixtures(*receivers: Callable, **fixtures: Dict[str, Callable]):
    """
    Create a new fixture provider which only returns fixtures from :obj:`fixtures`
    if they are requested by particular fixtures.
    """
    def _grouping(param_name: str, request_from: Callable):
        if param_name in fixtures and (request_from in receivers):
            return fixtures[param_name]

    return _grouping


class InstanceFixtureGroup(FixtureProvider, dict):
    """A dict which acts as a :class:`FixtureProvider`, providing it's instances as fixture values."""

    def __call__(self, name: str, _: Callable = None):
        if name in self:
            return lambda: self[name]

    def fixtures(self):
        return {name: self(name) for name in self}


class FixtureGroup(InstanceFixtureGroup):
    """A dict defining a group of fixture functions."""

    def __call__(self, name: str, _: Callable = None):
        if name in self:
            return self[name]
