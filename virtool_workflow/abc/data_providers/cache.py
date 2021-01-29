from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional, List


@dataclass(frozen=True)
class CacheEntry:
    database_id: Optional[str]
    trimming_parameters: Dict[str, Any]
    trimming_program: Dict[str, Any]
    files: List[dict]


class AbstractCacheProvider(ABC):

    @abstractmethod
    async def create(self, cache: CacheEntry):
        """Store a new cache entry."""
        ...

    @abstractmethod
    async def set_files(self, files: List[dict]):
        """Set the files included in the current cache."""
        ...

    @abstractmethod
    async def set_quality(self, quality: Dict[str, Any]):
        """Set the quality for the current cache and mark it as ready."""
        ...

    @abstractmethod
    async def find(self, trimming_parameters: Dict[str, Any], trimming_program: str) -> CacheEntry:
        """
        Find a cache entry for the current analysis which matches the trimming parameters and program being used.

        :param trimming_parameters: The parameters supplied to the `trimming_program` when.
        :param trimming_program: The program being used for trimming.
        :return: A cache entry for the current analysis, or None if there is no entry.
        """

    @abstractmethod
    async def delete_cache(self):
        """Delete the cache entry associated with the current analysis (in case it is incomplete, or invalid)."""
        ...

    @abstractmethod
    async def clear_caches(self):
        """Delete all caches associated with the sample being analyzed by the current job."""
        ...

    @abstractmethod
    async def unset_caches_for_analyses(self):
        """Invalidate all caches associated with this sample."""
        ...