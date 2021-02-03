"""Test utilities for Virtool Workflows."""
import pytest

from virtool_workflow.analysis.runtime import AnalysisWorkflowEnvironment
from virtool_workflow.data_model import Job
from virtool_workflow.storage.paths import context_directory


def testing_data_path():
    with context_directory("virtool") as data_path:
        yield data_path


@pytest.fixture
def runtime():
    with AnalysisWorkflowEnvironment(
            Job("test_job", {}),
    ) as _runtime:
        _runtime.override("data_path", testing_data_path)
        yield _runtime


__all__ = [
    "runtime",
]
