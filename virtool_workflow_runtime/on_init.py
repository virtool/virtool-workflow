import logging

from virtool_workflow import FixtureScope
from virtool_workflow_runtime.hooks import on_init

logger = logging.getLogger(__name__)


@on_init
def create_running_jobs_list(scope: FixtureScope):
    logger.debug("Creating `tasks` dictionaries.")
    scope["tasks"] = {}
