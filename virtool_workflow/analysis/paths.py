from pathlib import Path
from virtool_workflow import fixture
from typing import Dict, Any


@fixture
def sample_path(data_path: Path, job_args: Dict[str, Any]):
    """The sample path for the current job."""
    path = data_path/"subtractions"/job_args["sample_id"]
    path.mkdir(parents=True, exist_ok=True)
    return path


@fixture
def analysis_path(sample_path: Path, job_args: Dict[str, Any]) -> Path:
    """The analysis path for the current job."""
    path = sample_path/"analysis"/job_args["analysis_id"]
    path.mkdir(parents=True, exist_ok=True)
    return path


@fixture
def index_path(data_path: Path, job_args: Dict[str, Any]) -> Path:
    """The index path for the current job."""
    path = data_path/f"references/{job_args['ref_id']}/{job_args['index_id']}/reference"
    path.mkdir(parents=True, exist_ok=True)
    return path


@fixture
def raw_path(work_path) -> Path:
    """The raw path for the current job."""
    path = work_path / "raw"
    path.mkdir(parents=True, exist_ok=True)
    return path


@fixture
def temp_cache_path(work_path) -> Path:
    """The temp cache path for the current job."""
    path = work_path / "cache"
    path.mkdir(parents=True, exist_ok=True)
    return path


@fixture
def reads_path(work_path) -> Path:
    """The reads path for the current job."""
    path = work_path / "reads"
    path.mkdir(parents=True, exist_ok=True)
    return path


@fixture
def subtraction_data_path(data_path) -> Path:
    """Path to subtraction data."""
    path = data_path / "subtractions"
    path.mkdir(parents=True, exist_ok=True)
    return path


@fixture
def subtraction_path(work_path) -> Path:
    path = work_path / "subtractions"
    path.mkdir(parents=True, exist_ok=True)
    return path


__all__ = [
    "sample_path",
    "analysis_path",
    "raw_path",
    "index_path",
    "temp_cache_path",
    "reads_path",
    "subtraction_data_path",
    "subtraction_path",
]