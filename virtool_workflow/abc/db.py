from contextlib import AbstractAsyncContextManager

from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any, Optional


class DocumentUpdater(AbstractAsyncContextManager):

    @abstractmethod
    def set(self, key: str, value: Any):
        """
        Set the value of a field.

        The change will be applied when the :func:`update` method is called. 
        If the field does not exist a new one should be created, or an :obj:`ValueError`
        should be raised.

        :param key: The key of the field
        :type key: str
        :param value: The value to set the field to
        :type value: Any
        :raises ValueError: If the field does not exist and a new one cannot be created
        """
        ...

    @abstractmethod
    async def update(self):
        """Apply updates to the database."""
        ...

    async def __aexit__(self, exc_type, exc_value, trace):
        await self.update()


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
    def update(self, id: str) -> DocumentUpdater:
        """
        Retrieve a :class:`DocumentUpdater` for the document with the given id.

        The :class:`DocumentUpdater` instance can be used to modify the document.

        .. code-block:: python

            db: AbstractDatabaseCollection = ...
            my_id: str = ...
            async with db.update(my_id) as document:
                document.set("field", "value")
                ...
        """
        ...

    @abstractmethod
    async def delete(self, id: str):
        """Delete the document with the given id."""
        ...

