from collections import UserDict
from contextlib import AsyncExitStack, asynccontextmanager
from typing import Union
from ._fixture import Fixture

class FixtureScope(UserDict):
    """
    A container for fixture values. It functions as a regular Dict[str, Any]
    with additional method for binding fixture values.

    It also acts as an async context manager handling generator
    and async generator fixtures.
    """
    def __init__(self, *args, **instances):
        super(FixtureScope, self).__init__(*args, **instances)

        self._generators, self._async_generators = [], []

        self.open, self.closed = False, False

    async def __aenter__(self):
        """
        Creates a :class:`AsyncExitStack` where context managers
        can be added to handle generator and async generator fixtures.

        :return: This instance of :class:`FixtureScope`.
        """
        self._exit_stack = AsyncExitStack()
        return self


    async def __aexit__(self, *args):
        """
        Close this scope, ensuring that all generator and async generator
        fixtures are completed.
        """
        self._exit_stack.__aexit__(*args)

    async def instantiate(function: Union[callable, Fixture]):
        ...




