from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional


class AbstractDatabase(ABC):

    @abstractmethod
    async def fetch_document_by_id(self, id_: str, collection_name: str) -> Optional[Dict[str, Any]]:
        """Fetch the document with the given ID from a specific Virtool database collection."""
        ...

    async def find_document(self, collection_name: str, *args, **kwargs):
        """Find a document in a database collection based on the given query."""
        ...

    async def find_cache_document(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find a cache document using the given query."""
        ...

    @staticmethod
    async def create_cache_document(self, sample_id: str, trimming_parameters: Dict[str, Any],
                                    paired: bool, quality: Dict = None):
        """Create a new cache document."""
        ...

    async def delete_cache(self, cache_id: str):
        """Delete the cache with the given id."""
        ...

    async def delete_analysis(self, analysis_id: str):
        """Delete the analysis with the given id."""
        ...

    async def recalculate_workflow_tags_for_sample(self, sample_id):
        """Recalculate the workflow tags for a sample."""
        ...

    async def store_result(self, id_: str, result: Dict[str, Any], collection: str, file_results_location: Path):
        """Store the result onto the document specified by `id_` in the collection specified by `collection`."""
        ...

