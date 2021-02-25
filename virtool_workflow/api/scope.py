from .client import http_client
from .. import FixtureScope
from ..config.fixtures import jobs_api_url
from ..fixtures import FixtureGroup

api_fixtures = FixtureGroup(
    jobs_api_url=jobs_api_url,
    http_client=http_client,
)

api_scope = FixtureScope(api_fixtures)
