import pytest
import click
import click.testing
from virtool_workflow.config.group import ConfigFixtureGroup
from virtool_workflow.config.fixtures import options
from virtool_workflow.cli import cli


@pytest.fixture
def click_runner():
    return click.testing.CliRunner()


def test_fixture_group_adds_command_line_option():
    grp = ConfigFixtureGroup()

    @grp.fixture(type_=int, default=0)
    def some_config_option():
        """Some config option"""
        ...

    fixture = grp[some_config_option.__name__]

    assert fixture.name == fixture.__name__ == "some_config_option"
    assert fixture.type == int
    assert fixture.help == "Some config option"
    assert fixture.env == "VT_SOME_CONFIG_OPTION"


def test_fixture_group_can_be_applied_to_click_command(click_runner):
    @click.command()
    def command():
        ...

    grp = ConfigFixtureGroup()

    @grp.fixture
    def option():
        ...

    cmd = grp.add_options(command)

    result = click_runner.invoke(cmd, ["--help"])

    assert "--option" in result.output


def test_config_fixtures_get_added_as_options(click_runner):
    result = click_runner.invoke(cli, ["run", "--help"])

    for opt in ("--data-path", "--work-path"):
        assert opt in result.output
