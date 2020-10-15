from virtool_workflow import fixture
from .db import VirtoolDatabase


@fixture
def caches(database: VirtoolDatabase):
    return database["caches"]


@fixture
def samples(database: VirtoolDatabase):
    return database["samples"]


@fixture
def analyses(database: VirtoolDatabase):
    return database["analyses"]


@fixture
def jobs(database: VirtoolDatabase):
    return database["jobs"]