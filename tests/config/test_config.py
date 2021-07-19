import pytest
import click
import click.testing
from virtool_workflow.config.group import ConfigOptions
from virtool_workflow.cli import cli


@pytest.fixture
def click_runner():
    return click.testing.CliRunner()


def test_fixture_group_can_be_applied_to_click_command(click_runner):
    @click.command()
    def command():
        ...

    grp = ConfigOptions()

    @grp.fixture()
    def option():
        ...

    cmd = grp.add_options(command)

    result = click_runner.invoke(cmd, ["--help"])

    assert "--option" in result.output


def test_config_fixtures_get_added_as_options(click_runner):
    result = click_runner.invoke(cli, ["run", "--help"])

    for opt in ("--work-path", "--is-analysis-workflow"):
        assert opt in result.output
