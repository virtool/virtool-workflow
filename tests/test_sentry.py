"""Tests for Sentry configuration and context functions."""

from unittest.mock import MagicMock, mock_open, patch

import pytest
from pytest_mock import MockerFixture

from virtool_workflow.runtime.sentry import configure_sentry, set_workflow_context


class TestConfigureSentry:
    """Test the configure_sentry function."""

    def test_configure_sentry_with_dsn(self, mocker: MockerFixture) -> None:
        """Test that Sentry is initialized when DSN is provided."""
        mock_sentry_sdk = mocker.patch(
            "virtool_workflow.runtime.sentry.sentry_sdk",
        )
        mock_get_version = mocker.patch(
            "virtool_workflow.runtime.sentry.get_virtool_workflow_version",
        )

        mock_get_version.return_value = "9.1.0"
        dsn = "https://test@sentry.io/123"

        configure_sentry(dsn)

        mock_sentry_sdk.init.assert_called_once()
        init_args = mock_sentry_sdk.init.call_args[1]

        assert init_args["dsn"] == dsn
        assert init_args["release"] == "9.1.0"
        assert init_args["traces_sample_rate"] == 0.2

    def test_configure_sentry_without_dsn(self, mocker: MockerFixture) -> None:
        """Test that Sentry is not initialized when DSN is not provided."""
        mock_sentry_sdk: MagicMock = mocker.patch(
            "virtool_workflow.runtime.sentry.sentry_sdk",
        )

        configure_sentry("")

        mock_sentry_sdk.init.assert_not_called()

    def test_configure_sentry_with_none_dsn(self, mocker: MockerFixture) -> None:
        """Test that Sentry is not initialized when DSN is None."""
        mock_sentry_sdk: MagicMock = mocker.patch(
            "virtool_workflow.runtime.sentry.sentry_sdk",
        )
        configure_sentry(None)
        mock_sentry_sdk.init.assert_not_called()


class TestSetWorkflowContext:
    """Test the set_workflow_context function."""

    @pytest.mark.parametrize(
        ("version_content", "expected_version"),
        [
            ("1.2.3\n", "1.2.3"),
            ("  2.1.0-beta  \n", "2.1.0-beta"),
            ("\t3.0.0-rc1\t\n", "3.0.0-rc1"),
            ("0.1.0", "0.1.0"),
        ],
    )
    def test_set_workflow_context_with_version_file(
        self,
        mocker: MockerFixture,
        version_content: str,
        expected_version: str,
    ) -> None:
        """Test setting workflow context with version from file."""
        mock_sentry_sdk = mocker.patch(
            "virtool_workflow.runtime.sentry.sentry_sdk",
        )
        mock_get_version = mocker.patch(
            "virtool_workflow.runtime.sentry.get_virtool_workflow_version",
        )
        mock_get_version.return_value = "9.1.0"

        with patch("builtins.open", mock_open(read_data=version_content)):
            set_workflow_context("nuvs", "job_123")

        mock_sentry_sdk.set_context.assert_called_once_with(
            "workflow",
            {
                "workflow_name": "nuvs",
                "workflow_version": expected_version,
                "virtool_workflow_version": "9.1.0",
                "job_id": "job_123",
            },
        )

    def test_set_workflow_context_without_version_file(
        self,
        mocker: MockerFixture,
    ) -> None:
        """Test setting workflow context when VERSION file doesn't exist."""
        mock_sentry_sdk = mocker.patch(
            "virtool_workflow.runtime.sentry.sentry_sdk",
        )
        mock_get_version = mocker.patch(
            "virtool_workflow.runtime.sentry.get_virtool_workflow_version",
        )
        mock_get_version.return_value = "9.1.0"

        with patch("builtins.open", side_effect=FileNotFoundError()):
            set_workflow_context("build_index", "job_456")

        mock_sentry_sdk.set_context.assert_called_once_with(
            "workflow",
            {
                "workflow_name": "build_index",
                "workflow_version": "UNKNOWN",
                "virtool_workflow_version": "9.1.0",
                "job_id": "job_456",
            },
        )

    def test_set_workflow_context_different_workflow_types(
        self,
        mocker: MockerFixture,
    ) -> None:
        """Test setting context for different workflow types."""
        mock_sentry_sdk: MagicMock = mocker.patch(
            "virtool_workflow.runtime.sentry.sentry_sdk",
        )

        mock_get_version: MagicMock = mocker.patch(
            "virtool_workflow.runtime.sentry.get_virtool_workflow_version",
        )

        mock_get_version.return_value = "9.1.0"

        with patch("builtins.open", mock_open(read_data="1.0.0")):
            # Test analysis workflow
            set_workflow_context("pathoscope_bowtie", "analysis_job_123")

            # Test infrastructure workflow
            set_workflow_context("create_subtraction", "infra_job_456")

        assert mock_sentry_sdk.set_context.call_count == 2

        # Check first call (analysis workflow)
        first_call = mock_sentry_sdk.set_context.call_args_list[0]
        assert first_call[0][0] == "workflow"
        assert first_call[0][1]["workflow_name"] == "pathoscope_bowtie"
        assert first_call[0][1]["job_id"] == "analysis_job_123"

        # Check second call (infrastructure workflow)
        second_call = mock_sentry_sdk.set_context.call_args_list[1]
        assert second_call[0][0] == "workflow"
        assert second_call[0][1]["workflow_name"] == "create_subtraction"
        assert second_call[0][1]["job_id"] == "infra_job_456"
