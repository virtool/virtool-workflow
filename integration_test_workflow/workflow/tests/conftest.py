import pytest
from pathlib import Path


@pytest.fixture
def project_root() -> Path:
    return Path(__file__).parent.parent
