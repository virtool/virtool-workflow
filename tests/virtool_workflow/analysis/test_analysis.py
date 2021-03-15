from pathlib import Path

from virtool_workflow.abc.caches.analysis_caches import ReadsCache
from virtool_workflow.analysis.read_prep import reads
from virtool_workflow.analysis.reads import Reads
from virtool_workflow.analysis.utils import make_read_paths
from virtool_workflow.caching.local import LocalCacheWriter


async def test_get_reads_from_existing_cache(tmpdir, run_in_executor):
    tmpdir = Path(tmpdir)
    reads_cache_writer = LocalCacheWriter[ReadsCache]("read_cache", tmpdir, run_in_executor)

    mock_reads_file = tmpdir / "work/reads.fq.gz"
    mock_reads_file.parent.mkdir()
    mock_reads_file.touch()

    async with reads_cache_writer:
        await reads_cache_writer.upload(mock_reads_file)
        reads_cache_writer.quality = {
            "length": [0, 100],
            "count": 10
        }

    _reads = await reads(tmpdir / "reads", run_in_executor, False, reads_cache=reads_cache_writer.cache)

    assert isinstance(_reads, Reads)

    assert _reads.paired is False
    assert _reads.count == 10
    assert (_reads.min_length, _reads.max_length) == (0, 100)
    assert _reads.paths == make_read_paths(tmpdir / "reads", False)
