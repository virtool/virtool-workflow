from contextlib import contextmanager
from pathlib import Path
from typing import Union, AnyStr
from shutil import rmtree


@contextmanager
def context_directory(path: Union[Path, AnyStr]) -> Path:
    if not isinstance(path, Path):
        path = Path(path)

    path.mkdir()
    yield path
    rmtree(str(path))
