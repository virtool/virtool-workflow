from abc import ABC, abstractmethod
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

    @property
    @abstractmethod
    def analysis_provider(self) -> AbstractAnalysisProvider:
        ...

    @property
    @abstractmethod
    def caches_provider(self) -> AbstractCacheProvider:
        ...

    @property
    @abstractmethod
    def index_provider(self) -> AbstractIndexProvider:
        ...

    @property
    @abstractmethod
    def otus_provider(self) -> AbstractOTUsProvider:
        ...

    @property
    @abstractmethod
    def reference_provider(self) -> AbstractReferenceProvider:
        ...

    @property
    @abstractmethod
    def sample_provider(self) -> AbstractSampleProvider:
        ...

    @property
    @abstractmethod
    def subtraction_providers(self) -> Iterable[AbstractSubtractionProvider]:
        ...

    @property
    @abstractmethod
    def hmms_provider(self) -> AbstractHmmsProvider:
        ...


