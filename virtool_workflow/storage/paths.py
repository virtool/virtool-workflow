"""Fixtures and tools relating to paths."""
import logging
from contextlib import contextmanager
from pathlib import Path
from typing import Union, AnyStr
from shutil import rmtree

from virtool_workflow.fixtures.workflow_fixture import fixture

logger = logging.getLogger(__name__)


@contextmanager
def context_directory(path: Union[Path, AnyStr]) -> Path:
    """
    Context manager for a temporary directory.

    A new directory is created at the given path and will be deleted on exit.

    :param path: The path of a directory to create.
    :return: The Path of the newly created directory.
    """
    if not isinstance(path, Path):
        path = Path(path)

    root_path = path
    while not root_path.parent.exists():
        root_path = root_path.parent

    path.mkdir(parents=True, exist_ok=True)

    logger.info(f"Created temporary directory at {path}")

    try:
        yield path
    finally:
        rmtree(root_path)
        logger.info(f"Deleted temporary directory at {root_path}")


@fixture
def data_path(data_path_str: str):
    """Fetch the virtool data path."""
    _data_path = Path(data_path_str)
    if not _data_path.exists():
        _data_path.mkdir()
    return _data_path


@fixture
def temp_path(temp_path_str: str):
    """The virtool temp path."""
    with context_directory(temp_path_str) as temp:
        yield temp


@fixture
def cache_path(data_path: Path):
    """The virtool cache path."""
    _cache_path = data_path/"caches"
    if not _cache_path.exists():
        _cache_path.mkdir()
    return _cache_path


@fixture
def subtraction_data_path(data_path: Path):
    """The path locating subtraction data."""
    path = data_path/"subtractions"
    path.mkdir(parents=True, exist_ok=True)
    return path


@fixture
def subtraction_path(temp_path: Path):
    path = temp_path/"subtractions"
    path.mkdir(parents=True, exist_ok=True)
    return path

