from abc import ABC
from .analysis import AbstractAnalysisProvider
from .cache import AbstractCacheProvider


class AbstractDataProvider(ABC):
    analysis: AbstractAnalysisProvider
    caches: AbstractCacheProvider


