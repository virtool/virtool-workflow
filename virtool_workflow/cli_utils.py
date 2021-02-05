import click

from virtool_workflow.config.configuration import options


def apply_config_options(func):
    for option in options.values():
        func = click.option(option.option_name, type=option.type, help=option.help)(func)

    return func
