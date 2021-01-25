from virtool_workflow.analysis.analysis import analysis
from virtool_workflow.analysis.hmms import hmms
from virtool_workflow.analysis.indexes import indexes
from virtool_workflow.analysis.references.reference import reference
from virtool_workflow.analysis.samples.sample import sample
from virtool_workflow.analysis.subtractions.subtraction import subtractions
from virtool_workflow.data_model import Job
from virtool_workflow.fixtures import providers
from virtool_workflow.runtime import WorkflowEnvironment


class AnalysisWorkflowRuntime(WorkflowEnvironment):

    def __init__(self, job: Job):
        super(AnalysisWorkflowRuntime, self).__init__(job=job)

        self.load_plugins("virtool_workflow.analysis.fixtures")

        self.add_providers((
            providers.for_fixtures(analysis, analysis_provider=lambda: self.analysis_provider),
            providers.for_fixtures(sample, sample_provider=lambda: self.sample_provider),
            providers.for_fixtures(reference, reference_provider=lambda: self.reference_provider),
            providers.for_fixtures(indexes, index_provider=lambda: self.index_provider),
            providers.for_fixtures(subtractions, subtraction_providers=lambda: self.subtraction_providers),
            providers.for_fixtures(hmms, hmms_provider=lambda: self.hmms_provider)
        ))

