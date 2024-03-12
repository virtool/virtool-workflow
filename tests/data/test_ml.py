from pathlib import Path

import pytest
from pyfixtures import FixtureScope
from syrupy import SnapshotSession

from virtool_workflow.data.ml import WFMLModelRelease
from virtool_workflow.pytest_plugin.data import Data

test = SnapshotSession


class TestML:
    """Tests for the ML fixture that provides ML models for analyses."""

    @pytest.mark.parametrize("paired", [True, False], ids=["paired", "single"])
    async def test_ok(
        self,
        paired: bool,
        data: Data,
        example_path: Path,
        scope: FixtureScope,
    ):
        """Test that the ML fixture instantiates, contains the expected data, and
        downloads the sample files to the work path.
        """
        data.job.args["analysis_id"] = data.analysis.id

        data.analysis.workflow = "iimi"
        data.analysis.ml = data.ml

        ml: WFMLModelRelease = await scope.instantiate_by_key("ml")

        assert ml.id == data.ml.id
        assert ml.name == data.ml.name

        assert ml.path.is_dir()
        assert sorted([p.name for p in ml.path.iterdir()]) == [
            "mappability_profile.rds",
            "model.tar.gz",
            "nucleotide_info.csv",
            "reference.json.gz",
            "trained_rf.rds",
            "trained_xgb.rds",
            "virus_segments.rds",
        ]

    async def test_none(
        self,
        data: Data,
        scope: FixtureScope,
    ):
        """Test that the ML fixture returns None when no ML model is specified."""
        data.job.args["analysis_id"] = data.analysis.id

        data.analysis.ml = None
        data.analysis.workflow = "nuvs"

        ml: WFMLModelRelease = await scope.instantiate_by_key("ml")

        assert ml is None
