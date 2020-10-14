from dataclasses import dataclass
from pathlib import Path
from virtool_workflow import fixture
from virtool_workflow_runtime.db import VirtoolDatabase
from virtool_core.db.core import Collection


@dataclass(frozen=True)
class AnalysisJobInfo:
    path: Path
    sample_path: Path
    index_path: Path
    reads_path: Path
    subtraction_path: Path
    raw_path: Path
    temp_cache_path: Path
    temp_analysis_path: Path
    paired: bool
    read_count: int
    sample_read_length: int
    library_type: str


@fixture
def analysis_info(job_id: str, database: VirtoolDatabase, data_path: Path):
    jobs = database["jobs"]
    samples = database["samples"]
    analysis_db = database["analyses"]

    job = jobs.find_one(dict(_id=job_id))
    sample_id = job["sample_id"]
    analysis_id = job["analysis_id"]
    ref_id = job["ref_id"]
    index_id = job["index_id"]

    sample = await samples.find_one(dict(_id=sample_id))
    analysis_ = await analysis_db.find_one(dict(_id=analysis_id))

    sample_path = data_path/"samples"/sample_id

    return AnalysisJobInfo(
        path=sample_path/"analysis"/analysis_id,
        sample_path=sample_path,
        index_path=data_path/"references"/ref_id/index_id/"reference",
    )








