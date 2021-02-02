"""Central module for database access. """

from virtool_workflow.abc.db import AbstractDatabaseCollection


class VirtoolDatabase:

    def __init__(
            self,
            jobs: AbstractDatabaseCollection,
            analyses: AbstractDatabaseCollection,
            files: AbstractDatabaseCollection,
            hmms: AbstractDatabaseCollection,
            indexes: AbstractDatabaseCollection,
            otus: AbstractDatabaseCollection,
            references: AbstractDatabaseCollection,
            samples: AbstractDatabaseCollection,
            subtractions: AbstractDatabaseCollection,
    ):
        self.jobs = jobs
        self.analyses = analyses
        self.files = files
        self.hmms = hmms
        self.indexes = indexes
        self.otus = otus
        self.references = references
        self.samples = samples
        self.subtractions = subtractions
