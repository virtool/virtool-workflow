import pytest

import virtool_workflow.runtime.run_subprocess


@pytest.fixture()
def run_subprocess() -> virtool_workflow.runtime.run_subprocess.RunSubprocess:
    return virtool_workflow.runtime.run_subprocess.run_subprocess()
