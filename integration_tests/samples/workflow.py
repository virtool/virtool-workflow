import logging
from virtool_workflow import step
from virtool_workflow.analysis.reads import Reads
from virtool_workflow.data_model import Sample


@step
def fetch_sample(sample: Sample, logger: logging.Logger):
    assert sample.reads_path.exists()
    for read in sample.read_paths:
        assert read.exists()

    logger.info(sample)


@step
def fetch_reads(reads: Reads):
    assert reads.left.exists()
    assert reads.right.exists()
