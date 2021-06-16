from dataclasses import dataclass, field
from typing import List

from virtool_workflow.data_model.references import Reference


@dataclass
class Isolate:
    id: str
    source_name: str
    """The identifying part of the isolate name (eg. Canada-1)."""
    source_type: str
    """The common first part of the isolate name (eg. Isolate)"""


@dataclass
class Segment:
    molecule: str
    """The genome nucleic acid class (eg. dsRNA)."""
    name: str
    """The display name for the segment"""
    required: bool
    """A flag indicating that the segment is required for an isolate to pass validation."""


@dataclass
class OTU:
    id: str
    name: str
    """Display name of the OTU."""
    abbreviation: str
    """Abbreviated name of the OTU."""
    isolates: List[Isolate]
    """The isolates for the OTU."""
    reference: Reference
    """The parent reference."""
    version: int
    schema: List[Segment] = field(default_factory=lambda: [])
    """Definition of which segments should be in isolates of this OTU."""
    verified: bool = False
    """Flag indicating that the OTU has passed validation."""

    @property
    def lower_name(self) -> str:
        """
        The OTU name in all lower case.

        """
        return self.name.lower()
