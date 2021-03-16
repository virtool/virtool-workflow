from typing import Iterable

from virtool_workflow import hooks
from virtool_workflow.abc.data_providers import AbstractHMMsProvider, AbstractSubtractionProvider, \
    AbstractSampleProvider, AbstractOTUsProvider, AbstractIndexProvider, AbstractAnalysisProvider
from virtool_workflow.analysis.analysis import analysis
from virtool_workflow.analysis.hmms import hmms
from virtool_workflow.analysis.indexes import indexes
from virtool_workflow.analysis.samples.sample import sample
from virtool_workflow.analysis.subtractions.subtraction import subtractions
from virtool_workflow.data_model import Job
from virtool_workflow.environment import WorkflowEnvironment
from virtool_workflow.fixtures import providers
from virtool_workflow.fixtures.scope import FixtureScope


class DataProvider:

    def __init__(self,
                 scope: FixtureScope,
                 analysis_provider: AbstractAnalysisProvider = None,
                 index_provider: AbstractIndexProvider = None,
                 otus_provider: AbstractOTUsProvider = None,
                 sample_provider: AbstractSampleProvider = None,
                 subtraction_providers: Iterable[AbstractSubtractionProvider] = None,
                 hmms_provider: AbstractHMMsProvider = None):
        self.scope = scope
        self.analysis_provider = analysis_provider
        self.index_provider = index_provider
        self.otus_provider = otus_provider
        self.sample_provider = sample_provider
        self.subtraction_providers = subtraction_providers
        self.hmms_provider = hmms_provider

        scope.add_providers((
            providers.for_fixtures(
                analysis, analysis_provider=lambda: self.analysis_provider),
            providers.for_fixtures(
                sample, sample_provider=lambda: self.sample_provider),
            providers.for_fixtures(
                indexes, index_provider=lambda: self.index_provider),
            providers.for_fixtures(
                subtractions, subtraction_providers=lambda: self.subtraction_providers),
            providers.for_fixtures(
                hmms, hmms_provider=lambda: self.hmms_provider)
        ))


class AnalysisWorkflowEnvironment(WorkflowEnvironment):

    def __init__(self, job: Job,
                 analysis_provider: AbstractAnalysisProvider = None,
                 index_provider: AbstractIndexProvider = None,
                 otus_provider: AbstractOTUsProvider = None,
                 sample_provider: AbstractSampleProvider = None,
                 subtraction_providers: Iterable[AbstractSubtractionProvider] = None,
                 hmms_provider: AbstractHMMsProvider = None):
        super(AnalysisWorkflowEnvironment, self).__init__(job=job)
        self.load_plugins("virtool_workflow.analysis.fixtures")
        self.data_providers = DataProvider(self,
                                           analysis_provider,
                                           index_provider,
                                           otus_provider,
                                           sample_provider,
                                           subtraction_providers,
                                           hmms_provider)

        if analysis_provider:
            @hooks.on_success
            async def upload_results(results):
                await analysis_provider.upload_result(results)

            @hooks.on_failure
            async def delete():
                await analysis_provider.delete()
