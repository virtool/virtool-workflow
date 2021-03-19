import hashlib
import json
import shutil
from functools import partial
from pathlib import Path

from virtool_workflow import Workflow
from virtool_workflow.abc.caches.analysis_caches import ReadsCache
from virtool_workflow.analysis.read_prep.fastqc import fastqc
from virtool_workflow.analysis.read_prep.skewer import skewer
from virtool_workflow.analysis.utils import ReadPaths
from virtool_workflow.caching.caches import GenericCaches
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
        self.trimming_params = dict(
            mode=mode,
            max_error_rate=max_error_rate,
            max_indel_rate=max_indel_rate,
            end_quality=end_quality,
            mean_quality=mean_quality,
            number_of_processes=number_of_processes,
            quiet=quiet,
            other_options=other_options or ("-n", "-z")
        )
        self.skewer = partial(
            skewer,
            **self.trimming_params
        )

    async def __modify_workflow__(self, workflow: Workflow) -> Workflow:
        workflow.steps.insert(0, self.load_read_cache)
        return workflow

    async def _run_trimming(
            self,
            sample: Sample,
            run_subprocess: RunSubprocess,
            run_in_executor: FunctionExecutor,
    ):
        """
        Run skewer trimming for the sample.

        :obj:`sample.read_paths` and :obj:`sample.reads_path` will be updated
        to locate the trimmed fastq files.
        """
        run_skewer = self.skewer(sample.max_length)
        skewer_result = await run_skewer(sample.read_paths, run_subprocess, run_in_executor)
        sample.read_paths = skewer_result.read_paths

        return sample.read_paths

    async def _check_quality(
            self,
            read_paths: ReadPaths,
            work_path: Path,
            run_subprocess: RunSubprocess
    ):
        run_fastqc = fastqc(work_path, run_subprocess)
        return await run_fastqc(read_paths)

    async def load_read_cache(self,
                              sample: Sample,
                              sample_caches: GenericCaches[ReadsCache],
                              work_path: Path,
                              run_in_executor: FunctionExecutor,
                              run_subprocess: RunSubprocess):
        trim_param_json = json.dumps({
            "id": sample.id,
            "min_length": sample.min_length,
            **self.trimming_params,
        }, sort_keys=True)

        raw_key = "reads-" + trim_param_json

        key = hashlib.sha256(raw_key.encode()).hexdigest()

        try:
            cache = await sample_caches.get(key)
            await run_in_executor(shutil.copytree(cache.path, sample.reads_path))
        except KeyError:
            trimmed_reads = await self._run_trimming(sample, run_subprocess, run_in_executor)
            quality = await self._check_quality(sample.read_paths, work_path, run_subprocess)

            async with sample_caches.create(key) as cache:
                for path in trimmed_reads:
                    await cache.upload(path)

                cache.quality = quality
