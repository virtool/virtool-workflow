from abc import ABC
from typing import Iterable
from .analysis import AbstractAnalysisProvider
from .cache import AbstractCacheProvider
from .samples import AbstractSampleProvider
from .indexes import AbstractIndexProvider
from .otus import AbstractOTUsProvider
from .subtractions import AbstractSubtractionProvider
from .references import AbstractReferenceProvider
from .hmms import AbstractHmmsProvider


class AbstractDataProvider(ABC):
    def __new__(
            cls,
            *args,
            analysis_provider: AbstractAnalysisProvider = None,
            caches_provider: AbstractCacheProvider = None,
            index_provider: AbstractIndexProvider = None,
            otus_provider: AbstractOTUsProvider = None,
            reference_provider: AbstractReferenceProvider = None,
            sample_provider: AbstractSampleProvider = None,
            subtraction_providers: Iterable[AbstractSubtractionProvider] = None,
            hmms_provider: AbstractHmmsProvider = None,
            **kwargs
    ):
        obj = super(AbstractDataProvider, cls).__new__(*args, **kwargs)
        obj.analysis_provider = analysis_provider
        obj.caches_provider = caches_provider
        obj.index_provider = index_provider
        obj.otus_provider = otus_provider
        obj.reference_provider = reference_provider
        obj.sample_provider = sample_provider
        obj.subtraction_providers = subtraction_providers
        obj.hmms_provider = hmms_provider
        return obj


