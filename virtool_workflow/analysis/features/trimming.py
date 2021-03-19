from functools import partial

from virtool_workflow import Workflow
from virtool_workflow.analysis.read_prep.skewer import skewer
from virtool_workflow.data_model import Sample
from virtool_workflow.execution.run_in_executor import FunctionExecutor
from virtool_workflow.execution.run_subprocess import RunSubprocess
from virtool_workflow.features import WorkflowFeature


class Trimming(WorkflowFeature):

    def __init__(self,
                 mode: str = "pe",
                 max_error_rate: float = 0.1,
                 max_indel_rate: float = 0.03,
                 end_quality: int = 0,
                 mean_quality: int = 0,
                 number_of_processes: int = 1,
                 quiet: bool = True,
                 *other_options: str):
        self.skewer = partial(
            skewer,
            mode=mode,
            max_error_rate=max_error_rate,
            max_indel_rate=max_indel_rate,
            end_quality=end_quality,
            mean_quality=mean_quality,
            number_of_processes=number_of_processes,
            quiet=quiet,
            other_options=other_options or ("-n", "-z")
        )

    async def __modify_workflow__(self, workflow: Workflow) -> Workflow:
        workflow.step(self._run_trimming)
        return workflow

    async def _run_trimming(
            self,
            sample: Sample,
            run_subprocess: RunSubprocess,
            run_in_executor: FunctionExecutor,
    ):
        run_skewer = self.skewer(sample.max_length)
        skewer_result = await run_skewer(sample.read_paths, run_subprocess, run_in_executor)
        sample.read_paths = skewer_result.read_paths

        return "Completed Read Trimming."
