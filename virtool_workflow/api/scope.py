from .client import http_client
from .jobs import acquire_job
from .. import FixtureScope
from ..config.fixtures import jobs_api_url
from ..fixtures import FixtureGroup

api_fixtures = FixtureGroup(
    jobs_api_url,
    http_client,
    acquire_job
)

api_scope = FixtureScope(api_fixtures)
