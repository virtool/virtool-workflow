from virtool_workflow.fixtures.scope import FixtureScope
from virtool_workflow import hooks

from .fixtures import options


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
            option.override_value = (
                option.transform(kwargs[option.name]) or kwargs[option.name]
            )

    if not scope:
        async with FixtureScope(options) as config_scope:
            await hook.trigger(config_scope)
    else:
        scope.add_provider(options)
        await hook.trigger(scope)
