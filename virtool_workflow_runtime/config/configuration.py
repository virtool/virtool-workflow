import os
from dataclasses import dataclass

from virtool_workflow import WorkflowFixture


@dataclass(frozen=True)
class VirtoolConfiguration(WorkflowFixture, param_names=["config", "configuration"]):
    temp_path: str
    data_path: str
    proc: int
    mem: int
    redis_connection_string: str
    use_sentry: bool
    development_mode: bool
    mongo_database_name: str
    mongo_connection_string: str

    TEMP_PATH_ENV = "VT_TEMP_PATH"
    DATA_PATH_ENV = "VT_DATA_PATH"
    PROC_ENV = "VT_PROC"
    MEM_ENV = "VT_MEM"
    REDIS_CONNECTION_STRING_ENV = "VT_REDIS_CONNECTION_STRING"
    NO_SENTRY_ENV = "VT_NO_SENTRY"
    DEVELOPMENT_MODE_ENV = "VT_DEV"
    MONGO_DATABASE_CONNECTION_STRING_ENV = "VT_DB_CONNECTION_STRING"
    MONGO_DATABASE_NAME_ENV = "VT_DB_NAME"

    @classmethod
    def from_environment(cls,
                         temp_path: str = None,
                         data_path: str = None,
                         proc: int = None,
                         mem: int = None,
                         redis_connection_string: str = None,
                         use_sentry: bool = None,
                         development_mode: bool = None,
                         mongo_database_name: str = None,
                         mongo_connection_string: str = None
    ):
        return cls(
            temp_path=temp_path if temp_path else os.getenv(cls.TEMP_PATH_ENV),
            data_path=data_path if data_path else os.getenv(cls.DATA_PATH_ENV),

            proc=proc if proc else os.getenv(cls.PROC_ENV),
            mem=mem if mem else os.getenv(cls.MEM_ENV),

            use_sentry=use_sentry if use_sentry else os.getenv(cls.NO_SENTRY_ENV),
            development_mode=development_mode if development_mode else os.getenv(cls.DEVELOPMENT_MODE_ENV),

            redis_connection_string=(redis_connection_string if redis_connection_string
                                     else os.getenv(cls.REDIS_CONNECTION_STRING_ENV)),
            mongo_connection_string=(mongo_connection_string if mongo_connection_string
                                     else os.getenv(cls.MONGO_DATABASE_CONNECTION_STRING_ENV)),

            mongo_database_name=mongo_database_name if mongo_database_name else os.getenv(cls.MONGO_DATABASE_NAME_ENV),
        )

    @staticmethod
    def __fixture__() -> WorkflowFixture:
        return VirtoolConfiguration.from_environment()

