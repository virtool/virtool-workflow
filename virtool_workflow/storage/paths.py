"""Fixtures and tools relating to paths."""
from contextlib import contextmanager
from pathlib import Path
from typing import Union, AnyStr
from shutil import rmtree

from virtool_workflow import fixture


@contextmanager
def context_directory(path: Union[Path, AnyStr]) -> Path:
    """
    Context manager for a temporary directory.

    A new directory is created at the given path and will
    be deleted on exit.

    :param path: The path of a directory to create.
    :return: The Path of the newly created directory.
    """
    if not isinstance(path, Path):
        path = Path(path)

    path.mkdir(parents=True)
    yield path
    rmtree(path)


@fixture
def data_path():
    """Fetch the virtool data path."""
    # TODO: Get path from settings
    return Path("virtool")


@fixture
def temp_path():
    """The virtool temp path"""
    with context_directory("temp") as temp:
        yield temp


@fixture
def cache_path(data_path: Path):
    """The virtool cache path"""
    return data_path/"caches"
