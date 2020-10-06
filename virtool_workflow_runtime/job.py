from dataclasses import dataclass
from virtool_workflow import WorkflowExecutionContext, Workflow


@dataclass
class Job:
    """A Virtool Job

    :param id: The identifier used in this Job's database entry.
    :param workflow: The :class:`virtool_workflow.Workflow` being executed.
    :param context: The :class:`virtool_workflow.WorkflowExecutionContext of the Job.
    """
    id: str
    workflow: Workflow
    context: WorkflowExecutionContext = WorkflowExecutionContext()
