from typing import Any, NewType, Protocol, runtime_checkable

FixtureValue = NewType('FixtureValue', Any)
"""A return value from a :class:`Fixture` callable."""


@runtime_checkable
class Fixture(Protocol):
    """
    A Protocol formally defining any attributes which are 
    to a fixture function via @:func:`fixture`.

    Enables `isinstance(function, Fixture)` checks to be made.

    """
    __is_fixture__: bool = True

    async def __call__(self, *args, **kwargs) -> FixtureValue:
        ...
