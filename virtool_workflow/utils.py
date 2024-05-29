import asyncio
import tarfile
from collections.abc import Callable
from functools import wraps
from importlib import metadata
from inspect import iscoroutinefunction
from pathlib import Path


def coerce_to_coroutine_function(func: Callable):
    """Wrap a non-async function in an async function."""
    if iscoroutinefunction(func):
        return func

    @wraps(func)
    async def _func(*args, **kwargs):
        return func(*args, **kwargs)

    return _func


def get_virtool_workflow_version() -> str:
    return metadata.version("virtool-workflow")


async def make_directory(path: Path):
    await asyncio.to_thread(path.mkdir, exist_ok=True, parents=True)


def untar(path: Path, target_path: Path):
    with tarfile.open(path, "r:gz") as tar:
        tar.extractall(target_path)


def move_all_model_files(source_path: Path, target_path: Path):
    for file in source_path.iterdir():
        file.rename(target_path / file.name)
