"""Tests for Sentry configuration and context functions."""

import tempfile
import os
from unittest.mock import patch, mock_open, MagicMock
import pytest

from virtool_workflow.runtime.sentry import configure_sentry, set_workflow_context


class TestConfigureSentry:
    """Test the configure_sentry function."""

    @patch("virtool_workflow.runtime.sentry.sentry_sdk")
    @patch("virtool_workflow.runtime.sentry.get_virtool_workflow_version")
    def test_configure_sentry_with_dsn(self, mock_get_version, mock_sentry_sdk):
        """Test that Sentry is initialized when DSN is provided."""
        mock_get_version.return_value = "9.1.0"
        dsn = "https://test@sentry.io/123"

        configure_sentry(dsn)

        mock_sentry_sdk.init.assert_called_once()
        init_args = mock_sentry_sdk.init.call_args[1]
        assert init_args["dsn"] == dsn
        assert init_args["release"] == "9.1.0"
        assert init_args["traces_sample_rate"] == 0.2

    @patch("virtool_workflow.runtime.sentry.sentry_sdk")
    def test_configure_sentry_without_dsn(self, mock_sentry_sdk):
        """Test that Sentry is not initialized when DSN is not provided."""
        configure_sentry("")

        mock_sentry_sdk.init.assert_not_called()

    @patch("virtool_workflow.runtime.sentry.sentry_sdk")
    def test_configure_sentry_with_none_dsn(self, mock_sentry_sdk):
        """Test that Sentry is not initialized when DSN is None."""
        configure_sentry(None)

        mock_sentry_sdk.init.assert_not_called()


class TestSetWorkflowContext:
    """Test the set_workflow_context function."""

    @patch("virtool_workflow.runtime.sentry.sentry_sdk")
    @patch("virtool_workflow.runtime.sentry.get_virtool_workflow_version")
    def test_set_workflow_context_with_version(self, mock_get_version, mock_sentry_sdk):
        """Test setting workflow context with version."""
        mock_get_version.return_value = "9.1.0"

        set_workflow_context("nuvs", "job_123", "6.2.0")

        mock_sentry_sdk.set_context.assert_called_once_with(
            "workflow",
            {
                "workflow_name": "nuvs",
                "workflow_version": "6.2.0",
                "virtool_workflow_version": "9.1.0",
                "job_id": "job_123",
            },
        )

    @patch("virtool_workflow.runtime.sentry.sentry_sdk")
    @patch("virtool_workflow.runtime.sentry.get_virtool_workflow_version")
    def test_set_workflow_context_without_version(
        self, mock_get_version, mock_sentry_sdk
    ):
        """Test setting workflow context without version."""
        mock_get_version.return_value = "9.1.0"

        set_workflow_context("build_index", "job_456")

        mock_sentry_sdk.set_context.assert_called_once_with(
            "workflow",
            {
                "workflow_name": "build_index",
                "workflow_version": None,
                "virtool_workflow_version": "9.1.0",
                "job_id": "job_456",
            },
        )

    @patch("virtool_workflow.runtime.sentry.sentry_sdk")
    @patch("virtool_workflow.runtime.sentry.get_virtool_workflow_version")
    def test_set_workflow_context_different_workflow_types(
        self, mock_get_version, mock_sentry_sdk
    ):
        """Test setting context for different workflow types."""
        mock_get_version.return_value = "9.1.0"

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


class TestVersionFileReading:
    """Test VERSION file reading in run_workflow function."""

    @patch("virtool_workflow.runtime.run.set_workflow_context")
    @patch("virtool_workflow.runtime.run.acquire_job_by_id")
    @patch("virtool_workflow.runtime.run.api_client")
    @patch("virtool_workflow.runtime.run.create_work_path")
    @patch("virtool_workflow.runtime.run.ping_periodically")
    @patch("virtool_workflow.runtime.run.execute")
    @pytest.mark.parametrize("version_content,expected_version", [
        ("1.2.3\n", "1.2.3"),
        ("  2.1.0-beta  \n", "2.1.0-beta"),
        ("\t3.0.0-rc1\t\n", "3.0.0-rc1"),
        ("0.1.0", "0.1.0"),
    ])
    async def test_version_file_content_handling(
        self,
        mock_execute,
        mock_ping,
        mock_work_path,
        mock_api_client,
        mock_acquire_job,
        mock_set_context,
        version_content,
        expected_version,
    ):
        """Test that VERSION file content is properly stripped of whitespace."""
        from virtool_workflow.runtime.run import run_workflow
        from virtool_workflow.runtime.config import RunConfig
        from virtool_workflow.runtime.events import Events
        from virtool_workflow.workflow import Workflow

        # Mock job object
        mock_job = MagicMock()
        mock_job.id = "test_job_123"
        mock_job.workflow = "test_workflow"
        mock_job.key = "test_key"
        mock_acquire_job.return_value = mock_job

        # Mock API client context manager
        mock_api_client.return_value.__aenter__ = MagicMock()
        mock_api_client.return_value.__aexit__ = MagicMock()

        # Mock work path context manager
        mock_work_path.return_value.__aenter__ = MagicMock()
        mock_work_path.return_value.__aexit__ = MagicMock()

        # Mock ping context manager
        mock_ping.return_value.__aenter__ = MagicMock()
        mock_ping.return_value.__aexit__ = MagicMock()

        config = RunConfig(
            dev=False,
            jobs_api_connection_string="test://connection",
            mem=1000,
            proc=2,
            work_path="/tmp/test",
        )
        workflow = Workflow()
        events = Events()

        with patch("builtins.open", mock_open(read_data=version_content)):
            await run_workflow(config, "test_job_123", workflow, events)

        # Verify set_workflow_context was called with the properly stripped version
        mock_set_context.assert_called_once_with("test_workflow", "test_job_123", expected_version)

    @patch("virtool_workflow.runtime.run.set_workflow_context")
    @patch("virtool_workflow.runtime.run.acquire_job_by_id")
    @patch("virtool_workflow.runtime.run.api_client")
    @patch("virtool_workflow.runtime.run.create_work_path")
    @patch("virtool_workflow.runtime.run.ping_periodically")
    @patch("virtool_workflow.runtime.run.execute")
    async def test_version_file_not_found(
        self,
        mock_execute,
        mock_ping,
        mock_work_path,
        mock_api_client,
        mock_acquire_job,
        mock_set_context,
    ):
        """Test that 'UNKNOWN' is used when VERSION file doesn't exist."""
        from virtool_workflow.runtime.run import run_workflow
        from virtool_workflow.runtime.config import RunConfig
        from virtool_workflow.runtime.events import Events
        from virtool_workflow.workflow import Workflow

        # Mock job object
        mock_job = MagicMock()
        mock_job.id = "test_job_456"
        mock_job.workflow = "another_workflow"
        mock_job.key = "test_key"
        mock_acquire_job.return_value = mock_job

        # Mock API client context manager
        mock_api_client.return_value.__aenter__ = MagicMock()
        mock_api_client.return_value.__aexit__ = MagicMock()

        # Mock work path context manager
        mock_work_path.return_value.__aenter__ = MagicMock()
        mock_work_path.return_value.__aexit__ = MagicMock()

        # Mock ping context manager
        mock_ping.return_value.__aenter__ = MagicMock()
        mock_ping.return_value.__aexit__ = MagicMock()

        config = RunConfig(
            dev=False,
            jobs_api_connection_string="test://connection",
            mem=1000,
            proc=2,
            work_path="/tmp/test",
        )
        workflow = Workflow()
        events = Events()

        with patch("builtins.open", side_effect=FileNotFoundError()):
            await run_workflow(config, "test_job_456", workflow, events)

        # Verify set_workflow_context was called with "UNKNOWN" version
        mock_set_context.assert_called_once_with("another_workflow", "test_job_456", "UNKNOWN")
