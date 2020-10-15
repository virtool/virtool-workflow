from typing import Dict, Any, Optional

from virtool_workflow import fixture
from virtool_workflow_runtime.db.fixtures import caches, Collection
from .trim_parameters import trimming_parameters
from .analysis_info import sample_id
from virtool_core.caches.db import calculate_cache_hash
from virtool_core.db.utils import base_processor

TRIMMING_PROGRAM = "skewer-0.2.2"


@fixture
async def cache(
        trimming_parameters: Dict[str, Any],
        sample_id: str,
        caches: Collection,
) -> Optional[Dict[str, Any]]:
    return base_processor(caches.find_one({
        "hash": calculate_cache_hash(trimming_parameters),
        "missing": False,
        "program": TRIMMING_PROGRAM,
        "sample.id": sample_id
    }))
