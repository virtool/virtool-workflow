import pytest
from motor.motor_asyncio import AsyncIOMotorClient
from virtool_core.db.core import DB


@pytest.fixture
def connect_to_db(db_connection_string: str):
    def _dbi():
        client = AsyncIOMotorClient(db_connection_string)
        return DB(client["virtool"], None)

    return _dbi
