from integration_test_workflows import (
    test_hmms,
    test_indexes,
    test_sample,
    test_subtractions,
)
from virtool_workflow import features
from virtool_workflow.analysis.features.trimming import Trimming
from virtool_workflow.decorator_api import collect, step
from virtool_workflow.workflow import Workflow
from virtool_workflow.workflow_feature.merge_workflows import MergeWorkflows

features.install(
    Trimming(),
    MergeWorkflows(
        test_hmms,
        test_indexes,
        test_sample,
        test_subtractions,
    ),
)


@step
def test_results_available(results):
    assert results is not None
    assert isinstance(results, dict)
