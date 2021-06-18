from concurrent.futures.thread import ThreadPoolExecutor

import pytest

import virtool_workflow.execution.run_subprocess
import virtool_workflow.execution.run_in_executor


@pytest.fixture
def run_in_executor():
    return virtool_workflow.execution.run_in_executor.run_in_executor(
        ThreadPoolExecutor()
    )


@pytest.fixture
def run_subprocess():
    return virtool_workflow.execution.run_subprocess.run_subprocess()
