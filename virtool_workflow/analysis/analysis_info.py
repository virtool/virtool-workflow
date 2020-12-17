"""Workflow fixtures for use in analysis workflows."""
# pylint: disable=too-many-instance-attributes
# pylint: disable=redefined-outer-name
# pylint: disable=too-many-locals
# pylint: disable=arguments-differ
# pylint: disable=missing-function-docstring

from dataclasses import dataclass, astuple
from pathlib import Path
from typing import Dict, Any

from virtool_workflow import fixture, WorkflowFixture
from virtool_workflow.analysis import utils
from virtool_workflow.analysis.library_types import LibraryType
from virtool_workflow.db.db import fetch_document_by_id


@dataclass(frozen=True)
class AnalysisInfo(WorkflowFixture, param_name="analysis_info"):
    """Information from the Virtool database for analysis workflows."""
    sample_id: str
    analysis_id: str
    ref_id: str
    index_id: str
    sample: Dict[str, Any]
    analysis: Dict[str, Any]

    @staticmethod
    async def __fixture__(
            job_document: Dict[str, Any],
    ) -> "AnalysisInfo":
        """
        Fetch data related to an analysis job from the virtool database.

        :param job_document: The jobs document from the virtool database
        :return: A tuple containing the sample id, analysis id, reference id,
            index id, sample document, and analysis document.
        """
        sample_id = job_document["sample_id"]
        analysis_id = job_document["analysis_id"]
        ref_id = job_document["ref_id"]
        index_id = job_document["index_id"]

        sample = await fetch_document_by_id(sample_id, "samples")
        analysis_ = await fetch_document_by_id(analysis_id, "analyses")

        return AnalysisInfo(
            sample_id=sample_id,
            analysis_id=analysis_id,
            ref_id=ref_id,
            index_id=index_id,
            sample=sample,
            analysis=analysis_)


@dataclass(frozen=True)
class AnalysisArguments(WorkflowFixture, param_name="analysis_args"):
    """Dataclass containing standard arguments required for Virtool analysis workflows."""
    path: Path
    sample_path: Path
    index_path: Path
    reads_path: Path
    read_paths: utils.ReadPaths
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
        """
        Initialize AnalysisArguments based on information from the database.

        Any directories which do not yet exist will be created, so when this fixture
        fixture all path variables can be assumed to exist.

        """
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

        temp_cache_path = temp_path / "cache"

        args = AnalysisArguments(
            path=sample_path / "analysis" / analysis_id,
            sample_path=sample_path,
            index_path=data_path / "references" / ref_id / index_id / "reference",
            reads_path=reads_path,
            read_paths=read_paths,
            subtraction_path=subtraction_path,
            raw_path=temp_path / "raw",
            temp_cache_path=temp_cache_path,
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

        for path in [path for path in astuple(args) if isinstance(path, Path)]:
            path.mkdir(parents=True, exist_ok=True)

        return args


@fixture
def analysis_path(analysis_args: AnalysisArguments) -> Path:
    """The Virtool analysis path."""
    return analysis_args.path


@fixture
def sample_path(analysis_args: AnalysisArguments) -> Path:
    """The path to the sample data currently being analyzed."""
    return analysis_args.sample_path


@fixture
def index_path(analysis_args: AnalysisArguments) -> Path:
    """The Virtool index path."""
    return analysis_args.index_path


@fixture
def subtraction_path(analysis_args: AnalysisArguments) -> Path:
    return analysis_args.subtraction_path


@fixture
def raw_path(analysis_args: AnalysisArguments) -> Path:
    """Path to the raw read data (un-trimmed) for the current analysis."""
    return analysis_args.raw_path


@fixture
def temp_cache_path(analysis_args: AnalysisArguments) -> Path:
    """Path at which to store temporarily cached data."""
    return analysis_args.temp_cache_path


@fixture
def temp_analysis_path(analysis_args: AnalysisArguments) -> Path:
    """Path to store temporary analysis data."""
    return analysis_args.temp_analysis_path


@fixture
def paired(analysis_args: AnalysisArguments) -> bool:
    """A boolean indicating that the sequence currently being analyzed is paired."""
    return analysis_args.paired


@fixture
def read_count(analysis_args: AnalysisArguments) -> int:
    """The read count for the current sample."""
    return analysis_args.read_count


@fixture
def sample_read_length(analysis_args: AnalysisArguments) -> int:
    """The read length for the current sample."""
    return analysis_args.sample_read_length


@fixture
def library_type(analysis_args: AnalysisArguments) -> LibraryType:
    """The library type of the current sample data."""
    return analysis_args.library_type


@fixture
def sample(analysis_args: AnalysisArguments) -> Dict[str, Any]:
    """The sample database document for the current job."""
    return analysis_args.sample


@fixture
def analysis_document(analysis_args: AnalysisArguments) -> Dict[str, Any]:
    """The analysis database document for the current job."""
    return analysis_args.analysis


@fixture
def sample_id(analysis_args: AnalysisArguments) -> str:
    """The database ID of the sample being analyzed."""
    return analysis_args.sample_id


@fixture
def analysis_id(analysis_args: AnalysisArguments) -> str:
    """The database ID for the current analysis."""
    return analysis_args.analysis_id


@fixture
def ref_id(analysis_args: AnalysisArguments) -> str:
    """The database ID for the current reference."""
    return analysis_args.ref_id


@fixture
def index_id(analysis_args: AnalysisArguments) -> str:
    """The database ID for the current index."""
    return analysis_args.index_id
