from dataclasses import dataclass, field
from typing import List, Optional

from virtool_workflow.analysis.library_types import LibraryType


@dataclass
class Sample:
    """A Virtool Sample."""
    #: The sample's unique database ID.
    id: str
    #: A user-selected name.
    name: str
    #: A user-selected host of origin.
    host: str
    #: A user-selected isolate identifier.
    isolate: str
    #: A user-selected locale.
    locale: str
    #: The sample's :class:`.LibraryType`.
    library_type: LibraryType
    #: Flag indicating whether the Illumina data is paired.
    paired: bool
    #: A quality :class:`dict` from FastQC.
    quality: dict
    #: Flag indicating whether sample has a completed NuVs analysis.
    nuvs: bool = False
    #: Flag indicating whether sample has a completed Pathoscope analysis.
    pathoscope: bool = False
    #: Read files associated with the sample.
    files: List[dict] = field(default_factory=lambda: [])

    def __post_init__(self):
        self.reads_path = None
        self.read_paths = None

    @property
    def min_length(self) -> Optional[int]:
        """
        The minimum observed read length in the sample sequencing data.

        Returns ``None`` if the sample is still being created and no quality data is available.

        """
        return self.quality["length"][0] if self.quality else None

    @property
    def max_length(self) -> Optional[int]:
        """
        The maximum observed read length in the sample sequencing data.

        Returns ``None`` if the sample is still being created and no quality data is available.

        """
        return self.quality["length"][1] if self.quality else None
