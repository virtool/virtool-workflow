from dataclasses import dataclass
from virtool_workflow import WorkflowExecutionContext, Workflow


@dataclass
class Job:
    id: str
    workflow: Workflow
    context: WorkflowExecutionContext