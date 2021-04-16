from logging import Logger
from virtool_workflow import step
from virtool_workflow.data_model.samples import Sample
from virtool_workflow.features import install
from virtool_workflow.analysis.features.trimming import Trimming

install(Trimming())


@step
def test_sample_fixture_available():
    ...

