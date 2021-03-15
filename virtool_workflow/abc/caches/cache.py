from abc import abstractmethod, ABC
from contextlib import AbstractAsyncContextManager
from dataclasses import dataclass
from pathlib import Path


class CacheExists(Exception):
    ...


class CacheFileMissing(ValueError):
    ...


class CacheNotFinalized(ValueError):
    ...


@dataclass
class Cache:
    """Base class for all caches."""
    key: str
    """A key which will be used to retrieve the cache."""
    path: Path
    """Path to the directory containing cached files."""


class AbstractCacheWriter(AbstractAsyncContextManager):
    """Async context manager for creating new caches."""

    @property
    @abstractmethod
    def cache(self) -> Cache:
        """
        The cache which was created by this :class:`AbstractCacheWriter`.

        :raises CacheNotFinalized: When this property is accessed before the cache has been finalized.
        """

    @abstractmethod
    async def open(self):
        """
        Signal intent to create a new cache.

        :raises CacheExists: When there is already a cache open with a key matching :obj:`self.key`.
        """
        ...

    @abstractmethod
    async def upload(self, path: Path):
        """
        Upload a file to this cache.

        :param path: The path to a file to upload.
        :raises FileExistsError: When there is already a file in the cache with the same name.
        :raises IsADirectoryError: When the path given is a directory.
        """

        ...

    @abstractmethod
    async def close(self):
        """
        Finalize the cache.

        :raises ValueError: When a required value of the cache has not been set.
        :raises CacheFileMissing: When a required file for the cache has not been uploaded.
        """
        ...

    @abstractmethod
    async def delete(self):
        """Delete the cache."""
        ...

    async def __aenter__(self) -> "AbstractCacheWriter":
        """Open a new cache and return this :class:`AbstractCacheWriter`."""
        await self.open()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Finalize the cache and delete it upon any errors."""
        if exc_val:
            return await self.delete()

        try:
            return await self.close()
        except Exception as e:
            await self.delete()
            raise e


class AbstractCaches(ABC):

    @abstractmethod
    async def get(self, key: str) -> Cache:
        """
        Get the cache with a given key.

        :raises KeyError: When the given key does not map to an existing cache.
        """

    @abstractmethod
    def create(self, key: str) -> AbstractCacheWriter:
        """Create a new cache.

        :raises CacheExists: When a cache already exists for the given key.
        """
        ...

    @abstractmethod
    def __contains__(self, item: str):
        """Check if there is an existing cache with the given key."""
        ...
