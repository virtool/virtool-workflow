import logging

from virtool_workflow import FixtureScope
from virtool_workflow_runtime.cancellations import logger
from virtool_workflow_runtime.hooks import on_init

logger = logging.getLogger(__name__)


@on_init
def create_running_jobs_list(scope: FixtureScope):
    logger.debug("Creating `tasks` and `running_jobs` dictionaries.")
    scope["tasks"] = {}
    scope["running_jobs"] = {}
