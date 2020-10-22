"""Workflow fixtures from this module are implicitly loaded by the runtime"""
from virtool_workflow import analysis

__fixtures__ = [
    "virtool_workflow.execute",
    "virtool_workflow_runtime.db.db",
    "virtool_workflow_runtime.db.fixtures",
    "virtool_workflow_runtime.config.fixtures",
]
