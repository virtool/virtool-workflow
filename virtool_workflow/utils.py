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