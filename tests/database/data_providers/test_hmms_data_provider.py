from virtool_workflow.db.inmemory import InMemoryDatabaseCollection
from virtool_workflow.db.data_providers.hmms_data_provider import HmmsDataProvider


async def test_hmm_list():
    db = InMemoryDatabaseCollection()

    for _ in range(10):
        await db.insert({
            "families": {
                "Bunyaviridae": 4
            },
            "total_entropy": 50.4,
            "length": 90,
            "cluster": 3846,
            "entries": [
                {
                    "accession": "YP_004928150.1",
                    "gi": "356457880",
                    "organism": "Puumala virus",
                    "name": "nonstructural protein"
                },
                {
                    "accession": "YP_004928151.1",
                    "gi": "356457879",
                    "organism": "Andes virus",
                    "name": "putative nonstructural protein"
                },
                {
                    "accession": "YP_004928152.1",
                    "gi": "356218600",
                    "organism": "Sin Nombre virus",
                    "name": "putative nonstructural protein"
                },
                {
                    "accession": "YP_004928154.1",
                    "gi": "356460853",
                    "organism": "Tula virus",
                    "name": "nonstructral protein"
                }
            ],
            "genera": {
                "Hantavirus": 4
            },
            "mean_entropy": 0.56,
            "count": 4,
            "names": [
                "putative nonstructural protein",
                "nonstructural protein",
                "nonstructral protein"
            ],
            "hidden": False
        })

    provider = HmmsDataProvider(hmms=db)

    hmm_list = await provider.hmm_list()

    assert all(hmm.cluster for hmm in hmm_list)

