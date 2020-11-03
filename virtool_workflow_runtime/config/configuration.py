from dataclasses import dataclass


@dataclass(frozen=True)
class VirtoolConfiguration:
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

    def from_environment(self):
        pass