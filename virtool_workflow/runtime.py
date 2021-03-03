"""Main entrypoint(s) to run virtool workflows."""
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from virtool_workflow import discovery, FixtureScope
from virtool_workflow.analysis.runtime import AnalysisWorkflowEnvironment
from virtool_workflow.api.analysis import AnalysisProvider
from virtool_workflow.api.indexes import IndexProvider
from virtool_workflow.api.scope import api_fixtures
from virtool_workflow.config.configuration import load_config, config_fixtures
from virtool_workflow.environment import WorkflowEnvironment
from virtool_workflow.execution.hooks.fixture_hooks import FixtureHook
from virtool_workflow.fixtures import workflow_fixtures
from virtool_workflow.hooks import on_load_config

logger = logging.getLogger(__name__)

on_load_api = FixtureHook("on_load_api")


@on_load_config
def set_log_level_to_debug(dev_mode: bool):
    if dev_mode:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)


@on_load_config
def load_scripts(init_file: Path, fixtures_file: Path):
    if init_file.exists():
        discovery.import_module_from_file(module_name=init_file.name.rstrip(".py"), path=init_file)
    if fixtures_file.exists():
        discovery.import_module_from_file(module_name=fixtures_file.name.rstrip(".py"), path=fixtures_file)


@on_load_config
def extract_workflow(workflow_file_path: Path, scope):
    _workflow = discovery.discover_workflow(workflow_file_path)
    if not _workflow:
        raise RuntimeError(f"{workflow_file_path.name} does not contain a Workflow.")

    scope["workflow"] = _workflow


@on_load_api
async def init_environment(
        acquire_job,
        job_id,
        is_analysis_workflow,
        scope,
        http,
        jobs_api_url,
        work_path: Path,
):
    job = await acquire_job(job_id)

    if is_analysis_workflow:
        try:
            analysis_api = AnalysisProvider(
                job.args["analysis_id"], http, jobs_api_url
            )
        except KeyError:
            analysis_api = None

        try:
            index_path = work_path / f"indexes/{job.args['index_id']}"
            index_path.mkdir(parents=True, exist_ok=True)

            indexes_api = IndexProvider(
                index_id=job.args["index_id"],
                ref_id=job.args["ref_id"],
                index_path=index_path,
                http=http,
                jobs_api_url=jobs_api_url,
            )
        except KeyError:
            indexes_api = None

        scope["environment"] = AnalysisWorkflowEnvironment(job,
                                                           analysis_provider=analysis_api,
                                                           index_provider=indexes_api)
    else:
        scope["environment"] = WorkflowEnvironment(job)


@asynccontextmanager
async def prepare_environment(**config):
    scope = FixtureScope(config_fixtures)
    await load_config(scope=scope, **config)
    scope.add_providers(api_fixtures, workflow_fixtures)
    await on_load_api.trigger(scope)

    environment, workflow = scope["environment"], scope["workflow"]

    async with environment:
        yield environment, workflow


async def start(**config):
    async with prepare_environment(**config) as (environment, workflow):
        await environment.execute(workflow)
