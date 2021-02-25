import pytest
from motor.motor_asyncio import AsyncIOMotorClient
from virtool_core.db.core import DB


@pytest.fixture
def dbi(db_connection_string: str):
    client = AsyncIOMotorClient(db_connection_string)
    return DB(client["test"], None)
