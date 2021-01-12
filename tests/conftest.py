from virtool_workflow.storage.paths import data_path, context_directory

pytest_plugins = [
    "tests.fixtures.workflow",
    "tests.fixtures.scope",
    "tests.fixtures.execution",
    "tests.workflow_with_fixtures",
    "virtool_workflow_runtime.test_utils"
]


