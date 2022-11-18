from functools import wraps
from inspect import iscoroutinefunction
from logging import getLogger
from typing import Callable

logger = getLogger("runtime")


def coerce_to_coroutine_function(func: Callable):
    """Wrap a non-async function in an async function."""
    if iscoroutinefunction(func):
        return func

    @wraps(func)
    async def _func(*args, **kwargs):
        return func(*args, **kwargs)

    return _func
