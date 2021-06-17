from pathlib import Path

from virtool_workflow.abc.caches.analysis_caches import ReadsCache
from virtool_workflow.analysis.library_types import LibraryType
from virtool_workflow.analysis.reads import Reads, reads
from virtool_workflow.analysis.utils import make_read_paths
from virtool_workflow.caching.local import LocalCacheWriter
from virtool_workflow.data_model import Sample


async def test_get_reads_from_existing_cache(tmpdir, run_in_executor):
    tmpdir = Path(tmpdir)
    reads_path = tmpdir / "reads"
    reads_path.mkdir()
    reads_cache_writer = LocalCacheWriter[ReadsCache]("read_cache", reads_path, run_in_executor)

    mock_reads_file = tmpdir / "work/reads.fq.gz"
    mock_reads_file.parent.mkdir()
    mock_reads_file.touch()

    async with reads_cache_writer:
        await reads_cache_writer.upload(mock_reads_file)
        reads_cache_writer.quality = {
            "length": [0, 100],
            "count": 10
        }

    sample = Sample(
        id="foo",
        name="Foo",
        host="",
        isolate="",
        locale="",
        library_type=LibraryType.other,
        paired=False,
        quality=dict(),
        nuvs=False,
        pathoscope=False,
        files=[]
    )

    _reads = await reads(sample, reads_cache=reads_cache_writer.cache)

    assert isinstance(_reads, Reads)

    assert _reads.paired is False
    assert _reads.count == 10
    assert (_reads.min_length, _reads.max_length) == (0, 100)
    assert _reads.paths == make_read_paths(reads_path, False)
