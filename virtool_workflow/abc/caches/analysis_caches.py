from abc import ABC, abstractmethod

from virtool_workflow.abc.caches.cache import AbstractCache, CacheFileMissing


class AbstractAnalysisCache(ABC, AbstractCache):
    @property
    @abstractmethod
    def quality(self):
        """The parsed FastQC quality check output."""
        ...

    @quality.setter
    @abstractmethod
    def quality(self, qc: dict):
        ...

    async def close(self):
        if not self.quality:
            raise ValueError("FastQC quality check output must be provided.")

        cache_files = list(self.path.iterdir())

        if "reads.fq.gz" not in cache_files:
            if "reads_1.fq.gz" not in cache_files or "reads_2.fq.gz" not in cache_files:
                raise CacheFileMissing("Trimmed read files have not been uploaded to the read cache.")
