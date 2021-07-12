from typing import Protocol
from pathlib import Path


class FileDownloader(Protocol):
    async def __call__(self, id: str, target: Path) -> Path:
        """
        Download a file from Virtool's uploads API.

        :param id: The unique ID fo the file.
        :type id: str
        :param target: The path to which the file is downloaded.
        :type target: Path

        :returns: The target path, now locating the downloaded file.
        :rtype: Path
        """
