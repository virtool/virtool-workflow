from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass(frozen=True)
class CacheEntry:
    database_id: Optional[str]
    trimming_parameters: Dict[str, Any]
    trimming_program: Dict[str, Any]


class AbstractCacheProvider(ABC):

    @abstractmethod
    async def create(self):
        """Create and store a new cache entry."""
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