from typing import Iterable

from virtool_workflow.analysis.analysis import analysis
from virtool_workflow.analysis.hmms import hmms
from virtool_workflow.analysis.indexes import indexes
from virtool_workflow.analysis.references.reference import reference
from virtool_workflow.analysis.samples.sample import sample
from virtool_workflow.analysis.subtractions.subtraction import subtractions
from virtool_workflow.data_model import Job
from virtool_workflow.fixtures import providers
from virtool_workflow.runtime import WorkflowEnvironment
from virtool_workflow.abc.providers import AbstractDataProvider, AbstractHmmsProvider, AbstractSubtractionProvider, \
    AbstractSampleProvider, AbstractReferenceProvider, AbstractOTUsProvider, AbstractIndexProvider, \
    AbstractCacheProvider, AbstractAnalysisProvider
from virtool_workflow.fixtures.scope import FixtureScope


class ScopedDataProvider(AbstractDataProvider):

    def __init__(self,
                 scope: FixtureScope,
                 analysis_provider: AbstractAnalysisProvider = None,
                 caches_provider: AbstractCacheProvider = None,
                 index_provider: AbstractIndexProvider = None,
                 otus_provider: AbstractOTUsProvider = None,
                 reference_provider: AbstractReferenceProvider = None,
                 sample_provider: AbstractSampleProvider = None,
                 subtraction_providers: Iterable[AbstractSubtractionProvider] = None,
                 hmms_provider: AbstractHmmsProvider = None):
        self.scope = scope
        self._analysis_provider = analysis_provider
        self._caches_provider = caches_provider
        self._index_provider = index_provider
        self._otus_provider = otus_provider
        self._reference_provider = reference_provider
        self._sample_provider = sample_provider
        self._subtraction_providers = subtraction_providers
        self._hmms_provider = hmms_provider

        scope.add_providers((
            providers.for_fixtures(analysis, analysis_provider=lambda: self.analysis_provider),
            providers.for_fixtures(sample, sample_provider=lambda: self.sample_provider),
            providers.for_fixtures(reference, reference_provider=lambda: self.reference_provider),
            providers.for_fixtures(indexes, index_provider=lambda: self.index_provider),
            providers.for_fixtures(subtractions, subtraction_providers=lambda: self.subtraction_providers),
            providers.for_fixtures(hmms, hmms_provider=lambda: self.hmms_provider)
        ))

    @property
    def analysis_provider(self) -> AbstractAnalysisProvider:
        return self._analysis_provider

    @property
    def caches_provider(self) -> AbstractCacheProvider:
        return self._caches_provider

    @property
    def index_provider(self) -> AbstractIndexProvider:
        return self._index_provider

    @property
    def otus_provider(self) -> AbstractOTUsProvider:
        return self._otus_provider

    @property
    def reference_provider(self) -> AbstractReferenceProvider:
        return self._reference_provider

    @property
    def sample_provider(self) -> AbstractSampleProvider:
        return self._sample_provider

    @property
    def subtraction_providers(self) -> Iterable[AbstractSubtractionProvider]:
        return self._subtraction_providers

    @property
    def hmms_provider(self) -> AbstractHmmsProvider:
        return self._hmms_provider


class AnalysisWorkflowRuntime(WorkflowEnvironment):

    def __init__(self, job: Job):
        super(AnalysisWorkflowRuntime, self).__init__(job=job)

        self.load_plugins("virtool_workflow.analysis.fixtures")


