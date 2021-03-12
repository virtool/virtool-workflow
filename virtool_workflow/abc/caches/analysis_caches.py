from abc import abstractmethod

from virtool_workflow.abc.caches.cache import AbstractCacheWriter, CacheFileMissing


class AbstractReadsCache(AbstractCacheWriter):

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

        cache_files = list(p.name for p in self.path.iterdir())

        if "reads.fq.gz" not in cache_files:
            if "reads_1.fq.gz" not in cache_files or "reads_2.fq.gz" not in cache_files:
                raise CacheFileMissing("Trimmed read files have not been uploaded to the read cache.")

        await super(AbstractReadsCache, self).close()
