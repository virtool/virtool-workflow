from functools import partial
from pathlib import Path

from virtool_workflow import Workflow
from virtool_workflow.analysis.read_prep.skewer import skewer
from virtool_workflow.api.samples import SampleProvider
from virtool_workflow.environment import WorkflowEnvironment
from virtool_workflow.execution.run_in_executor import FunctionExecutor
from virtool_workflow.execution.run_subprocess import RunSubprocess
from virtool_workflow.features import WorkflowFeature


class Trimming(WorkflowFeature):

    def __init__(self,
                 mode: str,
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
        pass

    async def __modify_environment__(self, environment: WorkflowEnvironment):
        pass

    async def _run_trimming(
            self,
            sample_provider: SampleProvider,
            work_path: Path,
            run_subprocess: RunSubprocess,
            run_in_executor: FunctionExecutor,
    ):
        sample = await sample_provider.get()

        reads_path = work_path / "reads"
        reads_path.mkdir()

        await sample_provider.download_reads(reads_path, sample.paired)

        run_skewer = self.skewer(sample.max_length)
        await run_skewer(reads_path, run_subprocess, run_in_executor)
