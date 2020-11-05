from dataclasses import dataclass

from virtool_workflow import WorkflowFixture
from virtool_workflow.fixtures.scope import WorkflowFixtureScope
from virtool_workflow_runtime.config.environment import \
    temp_path_str, data_path_str, proc, mem, redis_connection_string, no_sentry, \
    dev_mode, db_name, db_connection_string


@dataclass(frozen=True)
class VirtoolConfiguration(WorkflowFixture, param_names=["config", "configuration"]):
    """Dataclass containing all configuration options."""
    temp_path: str
    data_path: str
    proc: int
    mem: int
    redis_connection_string: str
    no_sentry: bool
    development_mode: bool
    db_name: str
    db_connection_string: str

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
            no_sentry=no_sentry,
            development_mode=dev_mode,
            db_name=db_name,
            db_connection_string=db_connection_string
        )


def set_config_fixtures(config: VirtoolConfiguration, scope: WorkflowFixtureScope):
    """Set the values of all config related fixtures based on the values in a VirtoolConfiguration."""
    scope.add_instance(config.data_path, *data_path_str.param_names)
    scope.add_instance(config.temp_path, *temp_path_str.param_names)
    scope.add_instance(config.mem, *mem.param_names)
    scope.add_instance(config.proc, *proc.param_names)
    scope.add_instance(config.no_sentry, *no_sentry.param_names)
    scope.add_instance(config.development_mode, *dev_mode.param_names)
    scope.add_instance(config.db_name, *db_name.param_names)
    scope.add_instance(config.db_connection_string, *db_connection_string.param_names)
    scope.add_instance(config.redis_connection_string, *redis_connection_string.param_names)
    scope.add_instance(config, *config.param_names)


