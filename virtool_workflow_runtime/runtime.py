"""Main entrypoint(s) to the Virtool Workflow Runtime."""

import logging

from virtool_workflow import hooks
from virtool_workflow.config.configuration import DBType

_database = None


@hooks.on_load_config
def set_log_level_to_debug(config):
    if config.dev_mode:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)


@hooks.on_load_config
def instantiate_database(db_type: DBType):
    if db_type == "in-memory":
        _database =
