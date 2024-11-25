import asyncio
import logging
import sys
import tarfile
from collections.abc import Callable
from functools import wraps
from importlib import metadata
from inspect import iscoroutinefunction
from pathlib import Path

import structlog
from structlog.processors import LogfmtRenderer
from structlog_sentry import SentryProcessor


def coerce_to_coroutine_function(func: Callable):
    """Wrap a non-async function in an async function."""
    if iscoroutinefunction(func):
        return func

    @wraps(func)
    async def _func(*args, **kwargs):
        return func(*args, **kwargs)

    return _func


def configure_logs(use_sentry: bool):
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )

    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="%Y-%m-%dT%H:%M:%SZ"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    if use_sentry:
        processors.append(
            SentryProcessor(event_level=logging.WARNING, level=logging.INFO),
        )

    processors.append(
        LogfmtRenderer(
            key_order=["timestamp", "level", "logger", "event"],
        ),
    )

    structlog.configure(
        cache_logger_on_first_use=True,
        logger_factory=structlog.stdlib.LoggerFactory(),
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
    )


def get_virtool_workflow_version() -> str:
    """Get the version of the installed virtool-workflow package."""
    try:
        return metadata.version("virtool-workflow")
    except metadata.PackageNotFoundError:
        return "0.0.0"


async def make_directory(path: Path):
    await asyncio.to_thread(path.mkdir, exist_ok=True, parents=True)


def untar(path: Path, target_path: Path):
    with tarfile.open(path, "r:gz") as tar:
        tar.extractall(target_path)


def move_all_model_files(source_path: Path, target_path: Path):
    for file in source_path.iterdir():
        file.rename(target_path / file.name)
