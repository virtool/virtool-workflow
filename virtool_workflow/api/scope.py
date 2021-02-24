from .client import http_client
from .. import FixtureScope
from ..fixtures import FixtureGroup

api_fixtures = FixtureGroup(
    http_client
)

api_scope = FixtureScope(api_fixtures)
