from dataclasses import dataclass

from virtool_workflow.abc.caches.cache import Cache


@dataclass
class ReadsCache(Cache):
    quality: dict
