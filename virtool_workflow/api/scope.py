from .client import http
from .jobs import acquire_job, push_status
from .. import FixtureScope
from ..config.fixtures import jobs_api_url
from ..fixtures import FixtureGroup

api_fixtures = FixtureGroup(
    jobs_api_url,
    http,
    acquire_job,
    push_status
)

api_scope = FixtureScope(api_fixtures)
