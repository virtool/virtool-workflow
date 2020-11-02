from typing import Callable
from inspect import iscoroutinefunction
from functools import wraps


def coerce_to_coroutine_function(func: Callable):
    if iscoroutinefunction(func):
        return func

    @wraps(func)
    async def _func(*args, **kwargs):
        return func(*args, **kwargs)

    return _func


def coerce_coroutine_function_to_accept_any_parameters(func: Callable):

    @wraps(func)
    async def _func(*args, **kwargs):
        return await func()

    return _func