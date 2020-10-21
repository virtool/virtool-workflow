from virtool_workflow import fixture
from .db import Collection
from .db import VirtoolDatabase


@fixture
def caches(database: VirtoolDatabase) -> Collection:
    return database["caches"]


@fixture
def samples(database: VirtoolDatabase) -> Collection:
    return database["samples"]


@fixture
def analyses(database: VirtoolDatabase) -> Collection:
    return database["analyses"]


@fixture
def jobs(database: VirtoolDatabase) -> Collection:
    return database["jobs"]
