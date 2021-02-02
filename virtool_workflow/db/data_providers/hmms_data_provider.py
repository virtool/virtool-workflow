from virtool_workflow.abc.db import AbstractDatabaseCollection
from virtool_workflow.abc.data_providers import AbstractHmmsProvider
from typing import List
from virtool_workflow.data_model import HMM, HMMEntry


class HmmsDataProvider(AbstractHmmsProvider):

    def __init__(self, db: AbstractDatabaseCollection):
        self.db = db

    async def hmm_list(self) -> List[HMM]:
        documents = await self.db.find_by_projection(["cluster"])

        for document in documents:
            document["id"] = document["_id"]
            del document["_id"]

        return [
            HMM(**hmm)
            for hmm in documents
        ]
