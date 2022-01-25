import pytest
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient


@pytest.fixture
async def db(mongo_url, loop):
   """
   Prepare a MongoDB client for a test.

   The database will be dropped upon the completion of the test.
   """
   db_name = "test"
   client = AsyncIOMotorClient(mongo_url)
   await client.drop_database(db_name)

   try:
      yield client[db_name]
   finally:
      await client.drop_database(db_name)

