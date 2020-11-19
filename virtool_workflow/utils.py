from typing import Callable, Coroutine, Any
from inspect import iscoroutinefunction
from functools import wraps


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
