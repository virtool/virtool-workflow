from pathlib import Path

import arrow
import pytest

import virtool_workflow.runtime.run_subprocess
from virtool_workflow.pytest_plugin.data import (
    Data,
    data,
)


@pytest.fixture()
def run_subprocess() -> virtool_workflow.runtime.run_subprocess.RunSubprocess:
    return virtool_workflow.runtime.run_subprocess.run_subprocess()


@pytest.fixture()
def static_datetime():
    return arrow.get(2020, 1, 1, 1, 1, 1).naive


@pytest.fixture()
def virtool_workflow_example_path() -> Path:
    """The path to example data files for virtool-workflow."""
    return Path(__file__).parent.parent.parent / "example"


__all__ = [
    "data",
    "Data",
    "run_subprocess",
    "static_datetime",
    "virtool_workflow_example_path",
]
