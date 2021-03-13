from inspect import signature
from typing import TypeVar

from virtool_workflow.abc.caches.cache import Cache, AbstractCacheWriter, CacheNotFinalized

GenericCache = TypeVar("GenericCache", bound=Cache)


class GenericCacheWriter(AbstractCacheWriter):
    cache_class = Cache

    def __init__(self):
        self._attributes = {name: None for name
                            in signature(self.cache_class.__init__).parameters
                            if name != "self"}
        self._cache = None

    @property
    def cache(self) -> GenericCache:
        if not self._cache:
            raise CacheNotFinalized(
                f"Cache has missing attributes: {[key for key, value in self._attributes.items() if key is None]}"
            )
        return self._cache

    async def write_cache(self):
        ...

    def __setattr__(self, key, value):
        try:
            if key in self._attributes:
                self._attributes[key] = value
            else:
                raise KeyError(key)
        except (KeyError, AttributeError):
            super(GenericCacheWriter, self).__setattr__(key, value)

    async def _write(self):
        self._cache = self.cache_class(**self._attributes)
        await self.write_cache()

    async def open(self):
        return self

    async def close(self):
        await self._write()
        return await super(GenericCacheWriter, self).close()

    def __class_getitem__(cls, item):
        cls.cache_class = item
        return cls
