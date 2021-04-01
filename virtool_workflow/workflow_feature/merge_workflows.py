from virtool_workflow.workflow import Workflow
from virtool_workflow.features import WorkflowFeature


class MergeWorkflows(WorkflowFeature):
    """Merge steps from other workflows into the current workflow."""
    def __init__(self, *workflows: Workflow):
        self.workflows = workflows

    def __modify_workflow__(workflow: Workflow):
        return workflow.merge(*self.workflows)
