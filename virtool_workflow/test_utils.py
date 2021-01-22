from typing import Callable, Dict, Any

import pytest
import inspect

from virtool_workflow import WorkflowExecution, FixtureScope, Workflow
from virtool_workflow.analysis.runtime import AnalysisWorkflowRuntime
from virtool_workflow_runtime.runtime import runtime_scope
from virtool_workflow.storage.paths import context_directory
from virtool_workflow_runtime.config.configuration import data_path
from virtool_workflow.data_model import Job



@pytest.yield_fixture()
def runtime():
    """The WorkflowFixtureScope which would be used by the runtime."""
    test_environment = AnalysisWorkflowRuntime(job=Job("1", {}, 0, 1, [], ))

    with test_environment.scope:
        return test_environment
