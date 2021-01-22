"""Fixtures and tools relating to paths."""
import logging
from contextlib import contextmanager, suppress
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
        with suppress(FileNotFoundError):
            rmtree(root_path)
            logger.info(f"Deleted temporary directory at {root_path}")


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
def subtraction_path(work_path):
    path = work_path / "subtractions"
    path.mkdir(parents=True, exist_ok=True)
    return path


