"""Test utilities for Virtool Workflows."""

import pytest

from virtool_workflow.runtime import WorkflowEnvironment
from virtool_workflow.data_model import Job


@pytest.fixture
def runtime():
    return WorkflowEnvironment(Job("1", {}, 2, 2))
