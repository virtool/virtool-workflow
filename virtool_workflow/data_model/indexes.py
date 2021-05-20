from dataclasses import dataclass
from typing import Dict

from virtool_workflow.data_model.references import Reference


@dataclass
class Index:
    """A Virtool Index."""
    id: str
    manifest: Dict[str, int]
    reference: Reference
    ready: bool
