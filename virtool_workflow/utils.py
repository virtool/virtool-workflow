from typing import Callable, Coroutine, Any
from inspect import iscoroutinefunction
from functools import wraps, partial


class WrappedPartial:
    def __init__(self, func, *args, **kwargs):
        self.partial = partial(func, *args, **kwargs)
        self.__wrapped__ = func
        self.__name__ = func.__name__

    def __call__(self, *args, **kwargs):
        return self.partial(*args, **kwargs)

    def __str__(self):
        return str(self.__wrapped__)

    def __repr__(self):
        return str(self.__wrapped__)


def coerce_to_coroutine_function(func: Callable):
    """Wrap a non-async function in an async function."""
    if iscoroutinefunction(func):
        return func

    @wraps(func)
    async def _func(*args, **kwargs):
        return func(*args, **kwargs)

    return _func


def coerce_coroutine_function_to_accept_any_parameters(func: Callable[[], Coroutine[Any, Any, Any]]):
    """
    Wrap a coroutine function to ignore all parameters passed to it.

    :param func: A coroutine function which is callable without parameters.
    :return: A coroutine function which can take any parameters.
    """

    @wraps(func)
    async def _func(*args, **kwargs):
        return await func()

    return _func


def wrapped_partial(func, *args, **kwargs):
    return WrappedPartial(func, *args, **kwargs)
