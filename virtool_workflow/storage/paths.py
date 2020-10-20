from contextlib import contextmanager
from pathlib import Path
from typing import Union, AnyStr
from shutil import rmtree

from virtool_workflow import fixture


@contextmanager
def context_directory(path: Union[Path, AnyStr]) -> Path:
    if not isinstance(path, Path):
        path = Path(path)

    path.mkdir(parents=True, exist_ok=True)
    yield path
    rmtree(path)


@fixture
def data_path():
    """Fetch the virtool data path"""
    # TODO: Get path from settings
    return Path("virtool")


@fixture
def temp_path():
    with context_directory("temp") as temp:
        yield temp


@fixture
def cache_path(data_path: Path):
    return data_path/"caches"
