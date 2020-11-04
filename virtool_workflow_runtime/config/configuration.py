from dataclasses import dataclass
from virtool_workflow_runtime.config.fixtures import *


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

    @staticmethod
    def __fixture__(
            temp_path_str: str,
            data_path_str: str,
            proc: int,
            mem: int,
            redis_connection_string: str,
            no_sentry: bool,
            dev_mode: bool,
            db_name: str,
            db_connection_string: str
    ) -> WorkflowFixture:
        return VirtoolConfiguration(
            data_path=data_path_str,
            temp_path=temp_path_str,
            proc=proc,
            mem=mem,
            redis_connection_string=redis_connection_string,
            use_sentry=no_sentry,
            development_mode=dev_mode,
            mongo_database_name=db_name,
            mongo_connection_string=db_connection_string
        )


