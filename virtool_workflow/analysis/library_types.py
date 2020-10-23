"""Virtool library types."""
from enum import Enum, auto


class LibraryType(Enum):
    """Enum for Virtool library types."""
    amplicon = auto()
    srna = auto()
    other = auto()
