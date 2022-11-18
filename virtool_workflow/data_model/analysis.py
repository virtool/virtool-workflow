from pathlib import Path

from pydantic import PrivateAttr
from virtool_core.models.analysis import Analysis

from virtool_workflow import hooks
from virtool_workflow.data_model.files import VirtoolFileFormat


class WFAnalysis(Analysis):
    """
    Represents a Virtool analysis.

    Provides access to analysis data and a method :meth:`.upload` that allows selection
    of files in the workflow environment to be uploaded and associated with the analysis
    on workflow completion.

    """

    _to_upload: list = PrivateAttr(default_factory=list)

    def __init__(self, upload_files: callable, **kwargs):
        super().__init__(**kwargs)

        @hooks.on_success
        async def _upload_files():
            await upload_files(self._to_upload)
            self._to_upload = []

    def upload(self, path: Path, fmt: VirtoolFileFormat):
        """
        Mark a file to be uploaded at the end of a workflow run.

        :param path: the path to the file in the workflow work directory
        :param fmt: the format of the file being uploaded

        """
        self._to_upload.append((path, fmt))
