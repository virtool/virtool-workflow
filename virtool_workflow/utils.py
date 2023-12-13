import asyncio
from functools import wraps
from inspect import iscoroutinefunction
from pathlib import Path
from typing import Callable


def coerce_to_coroutine_function(func: Callable):
    """Wrap a non-async function in an async function."""
    if iscoroutinefunction(func):
        return func

    @wraps(func)
    async def _func(*args, **kwargs):
        return func(*args, **kwargs)

    return _func


async def make_directory(path: Path):
    await asyncio.to_thread(path.mkdir, exist_ok=True, parents=True)
