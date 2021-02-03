from virtool_workflow.config.configuration import config_fixture

REDIS_CONNECTION_STRING_ENV = "VT_REDIS_CONNECTION_STRING"
REDIS_JOB_LIST_NAME_ENV = "VT_REDIS_JOB_LIST_NAME"
NO_SENTRY_ENV = "VT_NO_SENTRY"
MONGO_DATABASE_CONNECTION_STRING_ENV = "VT_DB_CONNECTION_STRING"
MONGO_DATABASE_NAME_ENV = "VT_DB_NAME"


@config_fixture(env=REDIS_CONNECTION_STRING_ENV, default="redis://localhost:6379")
def redis_connection_string(_):
    """A fixture for the redis connection string/url."""
    ...


@config_fixture(REDIS_JOB_LIST_NAME_ENV, default="job_list")
def redis_job_list_name(_):
    """The name of the job list in redis."""
    ...


@config_fixture(env=NO_SENTRY_ENV, default=True)
def no_sentry(_):
    """A flag indicating whether or not to run sentry checks."""
    ...


@config_fixture(env=MONGO_DATABASE_NAME_ENV, default="virtool")
def db_name(_):
    """The MongoDB database name."""
    ...


@config_fixture(env=MONGO_DATABASE_CONNECTION_STRING_ENV, default="mongodb://localhost:27017")
def db_connection_string(_):
    """The MongoDB database connection string/url."""
    ...
