import os
from dataclasses import dataclass
from typing import Any, Type, Callable, Union

from virtool_workflow import hooks
from virtool_workflow.fixtures.providers import FixtureGroup
from virtool_workflow.fixtures.scope import FixtureScope


@dataclass(frozen=True)
class ConfigOption:
    name: str
    type: Type[Union[str, int, bool]]
    help: str
    fixture: "ConfigFixture"

    @property
    def option_name(self):
        return f"--{self.name}".replace("_", "-")


options = {}
config_fixtures = FixtureGroup()


class ConfigFixture(Callable):
    def __init__(self, name: str, env: str,
                 type_: Type[Union[str, int, bool]],
                 default: Any, help_: str, transform: Callable = None):
        self.name = name
        self.env = env
        self.type = type_
        self.default = default
        self.help = help_
        self.override_value = None
        self.transform = transform if transform else lambda x: x

        self.__name__ = self.name

        options[name] = ConfigOption(name=name, type=type_, help=help_, fixture=self)

    def __call__(self):
        if self.override_value:
            return self.override_value

        value = os.getenv(self.env, default=self.default)

        if self.type == bool:
            if value in ("True", "true", "Yes", "yes", "y", "Y"):
                return True
            else:
                return False

        if self.type == int:
            return int(value)

        transformed = self.transform(value)

        return transformed if transformed else value

    def __str__(self):
        return self.name


def config_fixture(
        env: str,
        type_: Type[Union[str, int, bool]] = str,
        default: Any = None,
        help_: str = "",
) -> Callable:
    def _config_fixture(transform: Callable[[Union[str, int, bool]], Any]):
        fixture = ConfigFixture(
            name=transform.__name__,
            env=env,
            type_=type_,
            default=default,
            help_=help_ if help_ else transform.__doc__,
            transform=transform
        )

        config_fixtures[fixture.name] = fixture

        return fixture

    return _config_fixture


async def load_config(scope=None, hook=None, **kwargs):
    """
    Override config fixture values with those from :obj:`kwargs`.

    Triggers `on_load_config` hook.

    :param kwargs: Values for any config options to be used before the fixtures.
    """
    if not hook:
        hook = hooks.on_load_config

    for option in options.values():
        if option.name in kwargs and kwargs[option.name] is not None:
            option.fixture.override_value = option.fixture.transform(kwargs[option.name]) or kwargs[option.name]

    if not scope:
        with FixtureScope(config_fixtures) as config_scope:
            await hook.trigger(config_scope)
    else:
        scope.add_provider(config_fixtures)
        await hook.trigger(scope)
