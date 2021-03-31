import click
from inspect import signature
from virtool_workflow.config.group import ConfigFixtureGroup


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


def test_fixture_group_can_be_aplied_to_click_command():
    @click.command
    def command():
        ...

    grp = ConfigFixtureGroup()

    @grp.fixture
    def option():
        ...

    cmd = grp.add_options(command)

    assert len(signature(cmd).parameters) == 1
