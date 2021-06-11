import logging
from virtool_workflow import step, fixture, features
from virtool_workflow.analysis.trimming import Trimming
from virtool_workflow.data_model import Sample

features.install(Trimming())


@fixture
def log():
    return logging.getLogger(__name__)


@step
def fetch_sample(sample: Sample, log: logging.Logger):
    assert sample.reads_path.exists()
    for read in sample.read_paths:
        assert read.exists()

    log.info(sample)
