from typing import Iterable
from virtool_workflow_runtime.discovery import load_fixtures_from__fixtures__

class WorkflowExecutionEnvironment:

    def __init__(self, fixture_plugins: Iterable[str]):