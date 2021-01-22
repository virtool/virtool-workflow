from typing import List

from virtool_workflow.analysis.hmms import hmms
from virtool_workflow.data_model import Job, Analysis, Sample, Reference, Index, Subtraction, HMM
from virtool_workflow.fixtures import providers
from virtool_workflow.runtime import WorkflowEnvironment


class AnalysisWorkflowRuntime(WorkflowEnvironment):

    def __init__(
            self,
            job: Job,
            analysis: Analysis = None,
            sample: Sample = None,
            reference: Reference = None,
            indexes: List[Index] = None,
            subtractions: List[Subtraction] = None,
            hmms_list: HMM = None,
    ):
        super(AnalysisWorkflowRuntime, self).__init__(job=job)

        self.load_plugins("virtool_workflow.analysis.fixtures")

        if analysis:
            self["analysis"] = analysis
        if sample:
            self["sample"] = sample
        if reference:
            self["reference"] = reference
        if indexes:
            self["indexes"] = indexes
        if subtractions:
            self["subtractions"] = subtractions
        if hmms_list:
            self.add_provider(
                providers.for_fixtures(hmms, hmms_list=lambda: hmms_list)
            )


