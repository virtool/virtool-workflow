"""Fixtures and tools relating to paths."""
import logging
from contextlib import contextmanager, suppress
from pathlib import Path
from typing import Union, AnyStr
from shutil import rmtree

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
