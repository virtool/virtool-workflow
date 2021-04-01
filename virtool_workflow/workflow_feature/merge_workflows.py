from virtool_workflow.workflow import Workflow
from virtool_workflow.features import WorkflowFeature
from virtool_workflow.decorator_api import collect
from typing import Union


class MergeWorkflows(WorkflowFeature):
    """Merge steps from other workflows into the current workflow."""
    def __init__(self, *workflows: Union[Workflow, ModuleType]):
        self.workflows = [workflow if isinstance(workflow, Workflow) else collect(workflow) for workflow in workflows]

    def __modify_workflow__(workflow: Workflow):
        return workflow.merge(*self.workflows)
