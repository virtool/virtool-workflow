import logging
from virtool_workflow import step, fixture, features
from virtool_workflow.analysis.reads import Reads
from virtool_workflow.data_model import Sample


@fixture
def log():
    return logging.getLogger(__name__)


@step
def fetch_sample(sample: Sample, log: logging.Logger):
    assert sample.reads_path.exists()
    for read in sample.read_paths:
        assert read.exists()

    log.info(sample)


@step
def fetch_reads(reads: Reads):
    for path in reads.paths:
        assert path.exists()

    # TODO: test other attirbutes of reads
