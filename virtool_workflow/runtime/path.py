import asyncio
from contextlib import asynccontextmanager
from pathlib import Path
from shutil import rmtree

from virtool_workflow.runtime.config import RunConfig


@asynccontextmanager
async def create_work_path(config: RunConfig) -> Path:
    """A temporary working directory where all workflow files should be written."""
    path = Path(config.work_path).absolute()

    await asyncio.to_thread(rmtree, path, ignore_errors=True)
    await asyncio.to_thread(path.mkdir, exist_ok=True, parents=True)

    yield path

    await asyncio.to_thread(rmtree, path)
