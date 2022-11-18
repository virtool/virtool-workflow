from pathlib import Path
from typing import Optional

from virtool_core.models.samples import Sample


class WFSample(Sample):
    """A Virtool Sample."""

    reads_path: Optional[Path] = None
    read_paths: Optional[Path] = None

    @property
    def min_length(self) -> Optional[int]:
        """
        The minimum observed read length in the sample sequencing data.

        Returns ``None`` if the sample is still being created and no quality data is available.

        """
        return self.quality.length[0] if self.quality else None

    @property
    def max_length(self) -> Optional[int]:
        """
        The maximum observed read length in the sample sequencing data.

        Returns ``None`` if the sample is still being created and no quality data is available.

        """
        return self.quality.length[1] if self.quality else None
