from abc import ABC
from .analysis import AbstractAnalysisProvider


class AbstractDataProvider(ABC):
    analysis: AbstractAnalysisProvider

