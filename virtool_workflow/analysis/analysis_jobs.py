from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Tuple

from virtool_workflow import fixture
from virtool_workflow.storage.paths import data_path, temp_path
from virtool_workflow_runtime.db import VirtoolDatabase


@dataclass(frozen=True)
class AnalysisArguments:
    path: Path
    sample_path: Path
    index_path: Path
    reads_path: Path
    read_paths: List[Path]
    subtraction_path: Path
    raw_path: Path
    temp_cache_path: Path
    temp_analysis_path: Path
    paired: bool
    read_count: int
    sample_read_length: int
    library_type: str
    sample: Dict[str, Any]
    analysis: Dict[str, Any]


AnalysisInfo = Tuple[str, str, str, str, Dict[str, Any], Dict[str, Any]]


@fixture
async def analysis_info(database: VirtoolDatabase,
                        job_id: str) -> AnalysisInfo:
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

    return (sample_id,
            analysis_id,
            ref_id,
            index_id,
            sample,
            analysis_)


@fixture
def analysis(
        analysis_info: Tuple,
        data_path: Path,
        temp_path: Path,
):
    (sample_id,
     analysis_id,
     ref_id,
     index_id,
     sample,
     analysis_) = analysis_info

    subtraction_id = analysis_["subtraction"]["id"].replace(" ", "_").lower()
    subtraction_path = data_path / "subtractions" / subtraction_id / "reference"

    sample_path = data_path / "samples" / sample_id
    reads_path = temp_path / "reads"

    read_paths = [reads_path / "reads_1.fq.gz"]

    paired = sample["paired"]

    if paired:
        read_paths.append(reads_path / "reads_2.fq.gz")

    return AnalysisArguments(
        path=sample_path / "analysis" / analysis_id,
        sample_path=sample_path,
        index_path=data_path / "references" / ref_id / index_id / "reference",
        reads_path=reads_path,
        read_paths=read_paths,
        subtraction_path=subtraction_path,
        raw_path=temp_path / "raw",
        temp_cache_path=temp_path / "cache",
        temp_analysis_path=temp_path / analysis_id,
        paired=sample["paired"],
        read_count=int(sample["quality"]["count"]),
        sample_read_length=int(sample["quality"]["length"][1]),
        library_type=sample["library_type"],
        sample=sample,
        analysis=analysis_
    )
