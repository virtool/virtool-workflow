import pytest
from virtool_core.db.core import DB


@pytest.fixture
def dbi():
    return DB()
