"""A fixture and dataclass for working with machine learning models in workflows."""
from dataclasses import dataclass
from pathlib import Path

from pyfixtures import fixture
from structlog import get_logger
from virtool_core.models.ml import MLModelRelease

from virtool_workflow.api.client import APIClient
from virtool_workflow.data.analyses import WFAnalysis
from virtool_workflow.utils import make_directory

logger = get_logger("api")


@dataclass
class WFMLModelRelease:
    """
    A machine learning model.

    This class represents a machine learning model and the selected release of that
    model in the workflow.
    """

    id: int
    """The unique ID for the model release."""

    name: str
    """The name of the model release."""

    path: Path
    """The path to the model directory."""

    @property
    def file_path(self) -> Path:
        """The path to the model data file."""
        return self.path / "model.tar.gz"


@fixture
async def ml(
    _api: APIClient, analysis: WFAnalysis, work_path: Path
) -> WFMLModelRelease | None:
    if analysis.ml is None:
        return None

    model_id = analysis.ml.model.id
    model_release_id = analysis.ml.id

    log = logger.bind(model_id=analysis.ml.id, model_release_id=model_release_id)

    model_release_json = await _api.get_json(
        f"/ml/{model_id}/releases/{model_release_id}"
    )
    model_release = MLModelRelease(**model_release_json)

    log.info("Fetched ML model release json")

    release = WFMLModelRelease(
        id=model_release.id,
        name=model_release.name,
        path=work_path / "ml" / str(model_release.model.id) / str(model_release_id),
    )

    await make_directory(release.path)

    await _api.get_file(
        f"/ml/{model_id}/releases/{model_release_id}/model.tar.gz", release.file_path
    )

    log.info("Downloaded ML model data file")

    return release
