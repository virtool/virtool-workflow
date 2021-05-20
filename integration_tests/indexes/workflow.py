from typing import List

from virtool_workflow import step, fixture
from virtool_workflow.analysis.indexes import Index


@fixture
def index(indexes: List[Index]):
    return indexes[0]


@step
def check_index(index: Index):
    assert index.path.exists()
    assert (index.path / "otus.json").exists()
    assert (index.path / "otus.json.gz").exists()


@step
async def build_index(index: Index):
    await index.build_isolate_index(
        list(index._sequence_otu_map.values()),
        f"{index.path}/reference",
        3,
    )

    for filename in (
        "reference.1.bt2",
        "reference.2.bt2",
        "reference.3.bt2",
        "reference.4.bt2",
        "reference.rev.1.bt2",
        "reference.rev.2.bt2",
        "reference.fa",
    ):
        assert (index.path / filename).exists()


@step
async def write_isolate_fasta(index: Index):
    path = index.path/"isolates_1"

    await index.write_isolate_fasta(
        list(index._sequence_otu_map.values()),
        path
    )

    assert path.exists()
