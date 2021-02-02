from abc import ABC, abstractmethod
from typing import Any, Optional, List, Iterable


class AbstractDatabaseCollection(ABC):

    @abstractmethod
    async def get(self, id: str) -> Optional[Any]:
        """Get the item with the given id."""
        ...

    @abstractmethod
    async def insert(self, value: Any) -> str:
        """
        Insert a new document into the database.

        :param value: The item to insert.
        :return: The id which can be used to access the item.
        """
        ...

    @abstractmethod
    async def set(self, id: str, **kwargs):
        """
        Set fields on the document identified by an ID.

        :param id: The ID identifying the document.
        :param kwargs: Key-value pairs to set on the document.
        """

    @abstractmethod
    async def delete(self, id: str):
        """Delete the document with the given id."""
        ...

    @abstractmethod
    async def find_by_projection(self, projection: List[str]) -> Iterable[Any]:
        """Find all documents which have all fields from the given projection."""

