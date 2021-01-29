from dataclasses import dataclass

from pathlib import Path
from typing import Dict

from virtool_workflow.data_model.references import Reference


@dataclass
class Index:
    """A Virtool Index."""
    id: str
    manifest: Dict[str, int]
    path: Path
    reference: Reference

