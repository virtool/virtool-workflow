from abc import abstractmethod
from inspect import signature
from typing import Generic, TypeVar, Type

from virtool_workflow.abc.caches.cache import Cache, AbstractCacheWriter, CacheNotFinalized

GenericCache = TypeVar("GenericCache", bound=Type[Cache])


class GenericCacheWriter(AbstractCacheWriter, Generic[GenericCache]):

    def __init__(self):
        self._attributes = {name: None for name in signature(GenericCache.__init__).parameters}
        self._cache = None

    @property
    def cache(self) -> GenericCache:
        if not self._cache:
            raise CacheNotFinalized(
                f"Cache has missing attributes: {[key for key, value in self._attributes.items() if key is None]}"
            )
        return self._cache

    @abstractmethod
    async def write_cache(self):
        ...

    def __setattr__(self, key, value):
        try:
            self._attributes[key] = value
        except KeyError:
            super(GenericCacheWriter, self).__setattr__(key, value)

    async def write(self):
        self._cache = GenericCache(**self._attributes)

        await self.write_cache()
