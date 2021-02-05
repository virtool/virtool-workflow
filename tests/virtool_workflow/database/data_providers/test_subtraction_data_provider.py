import pytest
from pathlib import Path

from virtool_workflow.data_model import NucleotideComposition
from virtool_workflow.db.data_providers.subtraction_data_provider import SubtractionDataProvider
from virtool_workflow.db.inmemory import InMemoryDatabaseCollection

TEST_SUBTRACTION = {
    "_id": "Apis mellifera",
    "nickname": "honey bee",
    "ready": True,
    "is_host": True,
    "file": {
        "id": "ii23chjh-GCF_003254395.2_Amel_HAv3.1_genomic.fa",
        "name": "GCF_003254395.2_Amel_HAv3.1_genomic.fa"
    },
    "user": {
        "id": "james"
    },
    "job": {
        "id": "98b12fh9"
    },
    "count": 177,
    "gc": {
        "a": 0.336,
        "t": 0.335,
        "g": 0.162,
        "c": 0.162,
        "n": 0.006
    },
    "name": "Apis mellifera",
    "deleted": False
}


@pytest.fixture
async def provider():
    subtractions = InMemoryDatabaseCollection()

    subtraction_id = await subtractions.insert(TEST_SUBTRACTION)

    return SubtractionDataProvider(subtraction_id, subtractions)


async def test_fetch_subtraction(provider: SubtractionDataProvider):
    subtraction_path = Path("")
    subtraction = await provider.fetch_subtraction(subtraction_path)

    assert subtraction.name == TEST_SUBTRACTION["name"]
    assert subtraction.gc == NucleotideComposition(**TEST_SUBTRACTION["gc"])
    assert subtraction.path == subtraction_path
