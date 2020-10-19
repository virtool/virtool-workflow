from dataclasses import dataclass, astuple
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

from virtool_workflow import fixture, WorkflowFixture
from virtool_workflow.analysis.library_types import LibraryType
from virtool_workflow_runtime.db import VirtoolDatabase
from virtool_workflow.storage.paths import data_path, temp_path
from virtool_workflow_runtime.db.fixtures import samples, analyses, jobs, Collection
from . import utils


@dataclass(frozen=True)
class AnalysisInfo:
    sample_id: str
    analysis_id: str
    ref_id: str
    index_id: str
    sample: Dict[str, Any]
    analysis: Dict[str, Any]


@fixture
async def analysis_info(
        job_document: Dict[str, Any],
        samples: Collection,
        analyses: Collection,
) -> AnalysisInfo:
    """
    Fetch data related to an analysis job from the virtool database.

    :param job_document: The jobs document from the virtool database
    :param samples: The samples collection from the virtool database
    :param analyses: The analyses collection from the virtool database
    :return: A tuple containing the sample id, analysis id, reference id,
        index id, sample document, and analysis document.
    """

    sample_id = job_document["sample_id"]
    analysis_id = job_document["analysis_id"]
    ref_id = job_document["ref_id"]
    index_id = job_document["index_id"]

    sample = await samples.find_one(dict(_id=sample_id))
    analysis_ = await analyses.find_one(dict(_id=analysis_id))

    return AnalysisInfo(
        sample_id=sample_id,
        analysis_id=analysis_id,
        ref_id=ref_id,
        index_id=index_id,
        sample=sample,
        analysis=analysis_)


@dataclass(frozen=True)
class AnalysisArguments(WorkflowFixture, param_name="analysis_args"):
    path: Path
    sample_path: Path
    index_path: Path
    reads_path: Path
    read_paths: utils.PairedPaths
    subtraction_path: Path
    raw_path: Path
    temp_cache_path: Path
    temp_analysis_path: Path
    paired: bool
    read_count: int
    sample_read_length: int
    library_type: LibraryType
    sample: Dict[str, Any]
    analysis: Dict[str, Any]
    sample_id: str
    analysis_id: str
    ref_id: str
    index_id: str

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
         analysis_) = astuple(analysis_info)

        subtraction_id = analysis_["subtraction"]["id"].replace(" ", "_").lower()
        subtraction_path = data_path / "subtractions" / subtraction_id / "reference"
        sample_path = data_path / "samples" / sample_id
        reads_path = temp_path / "reads"
        paired = sample["paired"]
        read_paths = utils.make_read_paths(reads_path, paired)

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
            analysis=analysis_,
            sample_id=sample_id,
            analysis_id=analysis_id,
            ref_id=ref_id,
            index_id=index_id,
        )


@fixture
def analysis_path(analysis_args: AnalysisArguments) -> Path:
    return analysis_args.path


@fixture
def sample_path(analysis_args: AnalysisArguments) -> Path:
    return analysis_args.sample_path


@fixture
def index_path(analysis_args: AnalysisArguments) -> Path:
    return analysis_args.index_path


@fixture
def reads_path(analysis_args: AnalysisArguments) -> Path:
    return analysis_args.reads_path


@fixture
def read_paths(analysis_args: AnalysisArguments) -> List[Path]:
    return analysis_args.read_paths


@fixture
def subtraction_path(analysis_args: AnalysisArguments) -> Path:
    return analysis_args.subtraction_path


@fixture
def raw_path(analysis_args: AnalysisArguments) -> Path:
    return analysis_args.raw_path


@fixture
def temp_cache_path(analysis_args: AnalysisArguments) -> Path:
    return analysis_args.temp_cache_path


@fixture
def temp_analysis_path(analysis_args: AnalysisArguments) -> Path:
    return analysis_args.temp_analysis_path


@fixture
def paired(analysis_args: AnalysisArguments) -> bool:
    return analysis_args.paired


@fixture
def read_count(analysis_args: AnalysisArguments) -> int:
    return analysis_args.read_count


@fixture
def sample_read_length(analysis_args: AnalysisArguments) -> int:
    return analysis_args.sample_read_length


@fixture
def library_type(analysis_args: AnalysisArguments) -> LibraryType:
    return analysis_args.library_type


@fixture
def sample(analysis_args: AnalysisArguments) -> Dict[str, Any]:
    return analysis_args.sample


@fixture
def analysis_document(analysis_args: AnalysisArguments) -> Dict[str, Any]:
    return analysis_args.analysis


@fixture
def sample_id(analysis_args: AnalysisArguments) -> str:
    return analysis_args.sample_id


@fixture
def analysis_id(analysis_args: AnalysisArguments) -> str:
    return analysis_args.analysis_id


@fixture
def ref_id(analysis_args: AnalysisArguments) -> str:
    return analysis_args.ref_id


@fixture
def index_id(analysis_args: AnalysisArguments) -> str:
    return analysis_args.index_id
