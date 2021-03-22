import hashlib
import json
import shutil
from functools import partial
from pathlib import Path

from virtool_workflow.abc.caches.analysis_caches import ReadsCache
from virtool_workflow.analysis.read_prep.fastqc import fastqc
from virtool_workflow.analysis.read_prep.skewer import skewer
from virtool_workflow.analysis.utils import make_read_paths
from virtool_workflow.api.samples import SampleProvider
from virtool_workflow.caching.caches import GenericCaches
from virtool_workflow.data_model import Sample
from virtool_workflow.environment import WorkflowEnvironment
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

    async def __modify_environment__(self, environment: WorkflowEnvironment):
        environment.override("sample", self._sample_fixture)

    async def _sample_fixture(self,
                              sample_provider: SampleProvider,
                              sample_caches: GenericCaches[ReadsCache],
                              work_path: Path,
                              run_subprocess: RunSubprocess,
                              run_in_executor: FunctionExecutor):
        """Alternate sample fixture which performs trimming and caching of reads."""
        sample = await sample_provider.get()
        key = self._compute_cache_key(sample)

        sample.reads_path = work_path / "reads"
        sample.reads_path.mkdir()
        sample.read_paths = make_read_paths(sample.reads_path, sample.paired)

        try:
            cache = await sample_caches.get(key)
        except KeyError:
            cache = await self._create_read_cache(key, sample, sample_caches,
                                                  work_path, run_subprocess, run_in_executor)

        await run_in_executor(shutil.copytree(cache.path, sample.reads_path))

        return sample

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

    async def load_or_create_read_cache(
            self,
            sample: Sample,
            sample_caches: GenericCaches[ReadsCache],
            work_path: Path,
            run_in_executor: FunctionExecutor,
            run_subprocess: RunSubprocess
    ):
        """
        Get trimmed reads from an existing cache if one exists.

        If not cache is found perform read trimming and create a new cache.
        """
        key = self._compute_cache_key(sample)
        try:
            cache = await sample_caches.get(key)
        except KeyError:
            cache = await self._create_read_cache(key, sample, sample_caches,
                                                  work_path, run_subprocess, run_in_executor)

        await run_in_executor(shutil.copytree(cache.path, sample.reads_path))

    def _compute_cache_key(self, sample):
        trim_param_json = json.dumps({
            "id": sample.id,
            "min_length": sample.min_length,
            **self.trimming_params,
        }, sort_keys=True)

        raw_key = "reads-" + trim_param_json

        return hashlib.sha256(raw_key.encode()).hexdigest()

    async def _create_read_cache(
            self,
            key: str,
            sample: Sample,
            sample_caches: GenericCaches[ReadsCache],
            work_path: Path,
            run_subprocess: RunSubprocess,
            run_in_executor: FunctionExecutor
    ):
        trimmed_reads = await self._run_trimming(sample, run_subprocess, run_in_executor)
        run_fastqc = fastqc(work_path, run_subprocess)
        quality = await run_fastqc(trimmed_reads)

        async with sample_caches.create(key) as cache:
            for path in trimmed_reads:
                await cache.upload(path)

            cache.quality = quality

            return cache
