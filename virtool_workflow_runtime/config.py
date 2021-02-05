from virtool_workflow.config.configuration import config_fixture

REDIS_CONNECTION_STRING_ENV = "VT_REDIS_CONNECTION_STRING"
REDIS_JOB_LIST_NAME_ENV = "VT_REDIS_JOB_LIST_NAME"
REDIS_CANCEL_LIST_NAME_ENV = "VT_CANCEL_LIST_NAME"
NO_SENTRY_ENV = "VT_NO_SENTRY"


@config_fixture(env=REDIS_CONNECTION_STRING_ENV, default="redis://localhost:6379")
def redis_connection_string(_):
    """A fixture for the redis connection string/url."""
    ...


@config_fixture(REDIS_JOB_LIST_NAME_ENV, default="job_list")
def redis_job_list_name(_):
    """The name of the job list in redis."""
    ...


@config_fixture(REDIS_CANCEL_LIST_NAME_ENV, default="cancel")
def redis_cancel_list_name(_):
    """The name of the redis list where cancellations are pushed."""
    ...


@config_fixture(env=NO_SENTRY_ENV, default=True)
def no_sentry(_):
    """A flag indicating whether or not to run sentry checks."""
    ...
