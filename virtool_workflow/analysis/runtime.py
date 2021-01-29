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
from virtool_workflow.abc.data_providers import AbstractHmmsProvider, AbstractSubtractionProvider, \
    AbstractSampleProvider, AbstractReferenceProvider, AbstractOTUsProvider, AbstractIndexProvider, \
    AbstractCacheProvider, AbstractAnalysisProvider
from virtool_workflow.fixtures.scope import FixtureScope


class DataProvider:

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
        self.analysis_provider = analysis_provider
        self.caches_provider = caches_provider
        self.index_provider = index_provider
        self.otus_provider = otus_provider
        self.reference_provider = reference_provider
        self.sample_provider = sample_provider
        self.subtraction_providers = subtraction_providers
        self.hmms_provider = hmms_provider

        scope.add_providers((
            providers.for_fixtures(
                analysis, analysis_provider=lambda: self.analysis_provider),
            providers.for_fixtures(
                sample, sample_provider=lambda: self.sample_provider),
            providers.for_fixtures(
                reference, reference_provider=lambda: self.reference_provider),
            providers.for_fixtures(
                indexes, index_provider=lambda: self.index_provider),
            providers.for_fixtures(
                subtractions, subtraction_providers=lambda: self.subtraction_providers),
            providers.for_fixtures(
                hmms, hmms_provider=lambda: self.hmms_provider)
        ))


class AnalysisWorkflowRuntime(WorkflowEnvironment):

    def __init__(self, job: Job,
                 analysis_provider: AbstractAnalysisProvider = None,
                 caches_provider: AbstractCacheProvider = None,
                 index_provider: AbstractIndexProvider = None,
                 otus_provider: AbstractOTUsProvider = None,
                 reference_provider: AbstractReferenceProvider = None,
                 sample_provider: AbstractSampleProvider = None,
                 subtraction_providers: Iterable[AbstractSubtractionProvider] = None,
                 hmms_provider: AbstractHmmsProvider = None):
        super(AnalysisWorkflowRuntime, self).__init__(job=job)
        self.load_plugins("virtool_workflow.analysis.fixtures")
        self.data_providers = DataProvider(self,
                                           analysis_provider,
                                           caches_provider,
                                           index_provider,
                                           otus_provider,
                                           reference_provider,
                                           sample_provider,
                                           subtraction_providers,
                                           hmms_provider)
