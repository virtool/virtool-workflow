"""Main entrypoint(s) to run virtool workflows."""
import logging

from virtool_workflow import hooks
from virtool_workflow.config.configuration import DBType
from virtool_workflow.db.inmemory import InMemoryDatabase
from virtool_workflow.db.mongo import VirtoolMongoDB

_database = None


@hooks.on_load_config
def set_log_level_to_debug(dev_mode):
    if dev_mode:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)


@hooks.on_load_config
def instantiate_database(db_type: DBType, db_name: str, db_connection_string: str):
    global _database
    if db_type == "in-memory":
        _database = InMemoryDatabase()
    elif db_type == "mongo":
        _database = VirtoolMongoDB(db_name, db_connection_string)
    elif db_type == "proxy":
        raise NotImplementedError("Proxy database is not yet supported.")
    else:
        raise ValueError(f"{db_type} is not a supported database type.")
