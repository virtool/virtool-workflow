from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Tuple

from virtool_workflow import fixture, WorkflowFixture
from virtool_workflow.storage.paths import data_path, temp_path
from virtool_workflow_runtime.db import VirtoolDatabase


AnalysisInfo = Tuple[str, str, str, str, Dict[str, Any], Dict[str, Any]]


@fixture
async def analysis_info(database: VirtoolDatabase,
                        job_id: str) -> AnalysisInfo:
    """
    Fetch data related to an analysis job from the virtool database.

    :param database: A connection to the Virtool database
    :param job_id: The id of the job document in the Virtool database
    :return: A tuple containing the sample id, analysis id, reference id,
        index id, sample document, and analysis document.
    """
    jobs = database["jobs"]
    samples = database["samples"]
    analysis_db = database["analyses"]

    job = await jobs.find_one(dict(_id=job_id))
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


@dataclass(frozen=True)
class AnalysisArguments(WorkflowFixture, param_name="analysis"):
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

    @staticmethod
    def __fixture__(
            data_path: Path,
            temp_path: Path,
            analysis_info: AnalysisInfo
    ) -> "AnalysisArguments":
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





