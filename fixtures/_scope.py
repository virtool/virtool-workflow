import inspect
from collections import UserDict
from contextlib import AsyncExitStack, asynccontextmanager, contextmanager
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
        self.exit_stack = await self._exit_stack.__aenter__()
        return self


    async def __aexit__(self, *args):
        """
        Close this scope, ensuring that all generator and async generator
        fixtures are completed.
        """
        await self._exit_stack.__aexit__(*args)

    async def _instantiate(self, function: Union[callable, Fixture], *args, **kwargs):
        """
        Get the return/yield value for the function.

        This function handles the following cases:

            - `function` is a coroutine function (async).
            - `function` is a normal, synchronous function.
            - `function` is an async generator function.
            - `function` is a (synchronous) generator function.

        In the case of generator (or async generator) functions,
        they will be converted into async context managers via :mod:`contextlib` 
        and added to the exit stack.

        :param args: arguments to forward to the function.
        :param kwargs: keyword arguments to forward to the function.

        :return: The return (or yield) value of `function`.
        """
        if inspect.isasyncgenfunction(function):
            ctx_manager = asynccontextmanager(function)
            return await self.exit_stack.enter_async_context(ctx_manager(*args, **kwargs))

        if inspect.isgeneratorfunction(function):
            ctx_manager = contextmanager(function)
            return self.exit_stack.enter_context(ctx_manager(*args, **kwargs))
        
        if inspect.iscoroutinefunction(function):
            return await function(*args, **kwargs)

        # Must be a synchronous function.
        return function(*args, **kwargs)



    async def instantiate(self, function: Union[callable, Fixture]):
        ...




