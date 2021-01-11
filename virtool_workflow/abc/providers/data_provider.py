from abc import ABC
from typing import Iterable
from .analysis import AbstractAnalysisProvider
from .cache import AbstractCacheProvider
from .samples import AbstractSampleProvider
from .indexes import AbstractIndexProvider
from .otus import AbstractOTUsProvider
from .subtractions import AbstractSubtractionProvider
from .references import AbstractReferenceProvider


class AbstractDataProvider(ABC):
    analysis: AbstractAnalysisProvider
    caches: AbstractCacheProvider
    sample: AbstractSampleProvider
    index: AbstractIndexProvider
    otus: AbstractOTUsProvider
    reference: AbstractReferenceProvider
    subtractions: Iterable[AbstractSubtractionProvider]


