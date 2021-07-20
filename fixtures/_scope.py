
import inspect
from collections import UserDict
from contextlib import (AsyncExitStack, asynccontextmanager, contextmanager,
                        suppress)
from functools import wraps
from typing import Any, Dict, Union

from ._fixture import Fixture, get_fixtures
from ._utils import get_arg_spec, get_defaults
from .errors import FixtureBindingError, FixtureNotFound, FixtureHasDependency


class FixtureScope(UserDict):
    """
    A container for fixture values. It functions as a regular Dict[str, Any]
    with additional methods for binding fixture values.

    It also acts as an async context manager handling generator
    and async generator fixtures.
    """
    async def __aenter__(self):
        """
        Creates a :class:`AsyncExitStack` where context managers
        can be added to handle generator and async generator fixtures.

        :return: This instance of :class:`FixtureScope`.
        """
        self["scope"] = self
        self.exit_stack = await AsyncExitStack().__aenter__()
        return self

    async def __aexit__(self, *args):
        """
        Close the :class:FixtureScope.

            1. Remove all references to fixture values.
            2. Close the exit stack, ensuring that generator fixtures are closed out.
        """
        self.clear()
        await self.exit_stack.__aexit__(*args)

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
        try:
            if inspect.isasyncgenfunction(function):
                return await self.exit_stack.enter_async_context(
                    asynccontextmanager(function)(*args, **kwargs)
                )

            if inspect.isgeneratorfunction(function):
                return self.exit_stack.enter_context(
                    contextmanager(function)(*args, **kwargs)
                )

            if inspect.iscoroutinefunction(function):
                return await function(*args, **kwargs)

            # Must be a synchronous function..
            return function(*args, **kwargs)
        except TypeError as e:
            if "missing" in str(e):
                raise FixtureHasDependency() from e
            raise

    @property
    def available(self) -> Dict[str, Any]:
        """A dict of all available fixtures."""
        fixtures = get_fixtures()
        return dict(fixtures, **self)

    @staticmethod
    def _bind(
        function: callable,
        argspec: inspect.FullArgSpec,
        values: dict,
    ) -> callable:
        """
        Bind values to function parameters.

        :param function: The function to bind.
        :param argspec: The argspec for the function, obtained
                        via :func:`inspect.getfullargspec`.
        :param values: Key value pairs to bind to the function.

        :return: The bound function.
        """
        def prep_args(args, kwargs):
            if args or kwargs:
                # Since `values` is stored in the closure
                # updates to it will persist between calls
                _values = values.copy()
            else:
                _values = values

            # Support using keyword arguments when calling `_bound`
            _values.update(kwargs)

            # Support using positional arguments when calling `_bound`
            if args:
                # Remove supplied args from the `values`
                arg_names = argspec.args[:len(args)]
                for name in arg_names:
                    del _values[name]

            return args, _values

        if inspect.isgeneratorfunction(function):
            @wraps(function)
            def _bound(*args, **kwargs):
                _args, _kwargs = prep_args(args, kwargs)
                yield from function(*_args, **_kwargs)
        elif inspect.isasyncgenfunction(function):
            @wraps(function)
            async def _bound(*args, **kwargs):
                _args, _kwargs = prep_args(args, kwargs)
                asyncgen = await function(*_args, **_kwargs)
                async for item in asyncgen:
                    yield item
        elif inspect.iscoroutinefunction(function):
            @wraps(function)
            async def _bound(*args, **kwargs):
                _args, _kwargs = prep_args(args, kwargs)
                return await function(*_args, **_kwargs)
        else:
            @wraps(function)
            def _bound(*args, **kwargs):
                _args, _kwargs = prep_args(args, kwargs)
                return function(*_args, **_kwargs)

        return _bound

    async def bind(
        self,
        function: Union[callable, Fixture],
        follow_wrapped: bool = True,
        **kwargs: Any,
    ) -> Union[callable, Fixture]:
        """
        Instantiate fixtures as needed based on the signature of
        `function`. Wrap `function` to pass the fixture values as
        parameters where needed.

        This function will try to get a value for each key with the following priority:

            :first:
                Values from `**kwargs`. if one is present for the given key then
                the corresponding fixture would not be instantiated.

            :second:
                If no value is present in `**kwargs` the fixture will be instantiated
                and it's return value will be used.

            :third:
                If the fixture cannot be instantiated, the default value for the
                parameter (on the fixture function) will be used if it exists.

        :param function: The function to bind fixtures to.
        :param follow_wrapped: Use the signature of the wrapped function
                               instead of the outer function, defaults to False
        :param kwargs: Additional keyword arguments to bind to the function.
                       This will be used instead of the fixture value when there
                       is a name collision.
        :raise FixtureBindingError: When a required fixture cannot be found or instantiated.

        :return: A function wrapping `function` which does not require arguments.
                 If arguments are given they will overwrite the bound fixture values.
        """
        if hasattr(function, "__follow_wrapped__"):
            follow_wrapped = function.__follow_wrapped__

        argspec = get_arg_spec(function, follow_wrapped)

        if argspec.varargs is not None or argspec.varkw is not None:
            raise FixtureBindingError(
                function, argspec.varargs,
                reason="Binding fixtures to `*args` or `**kwargs` is not supported."
            )

        if len(argspec.args) == 0:
            return function

        defaults = get_defaults(argspec)

        for key in argspec.args:
            if key in kwargs:
                continue

            try:
                kwargs[key] = await self.instantiate_by_key(key)
            except Exception as e:
                if key in defaults:
                    kwargs[key] = defaults[key]
                    continue

                raise FixtureBindingError(
                    function, key,
                    reason=f"Could not instantiate `{key}` due to {e.__class__.__name__}"
                ) from e

        return self._bind(function, argspec, kwargs)

    async def instantiate_by_key(self, key: str, *args, **kwargs) -> Any:
        """Instantiate a fixture by it's name."""
        with suppress(KeyError):
            return self[key]

        fixtures = get_fixtures()
        try:
            fixture = fixtures[key]
        except KeyError:
            raise FixtureNotFound(key, self)

        return await self.instantiate(fixture, *args, **kwargs)

    async def get_or_instantiate(
        self,
        fixture: Union[str, callable, Fixture],
        *args: Any,
        **kwargs: Any,
    ):
        """Instantiate a fixture by name, or directly."""
        if isinstance(fixture, str):
            return await self.instantiate_by_key(fixture, *args, **kwargs)
        else:
            return await self.instantiate(fixture, *args, **kwargs)

    async def instantiate(self, fixture: Fixture, *args, **kwargs):
        """
        Instantiate a given fixture and add it to the scope.

        Recursively bind parameters of the function as required.

        :param function: The function/fixture to instantiate.
        :return: The fixture's value.
        """
        with suppress(KeyError):
            return self[fixture.__name__]

        try:
            value = await self._instantiate(fixture, *args, **kwargs)
        except FixtureHasDependency:
            value = await self.instantiate(await self.bind(fixture, follow_wrapped=True), *args, **kwargs)

        self[fixture.__name__] = value

        return value
