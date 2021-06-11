import asyncio
import docker
import logging
from pathlib import Path

from virtool_workflow.data_model import Job
from virtool_workflow_runtime._docker import start_workflow_container
from virtool_workflow_runtime.hooks import on_start, on_init, on_docker_event, on_docker_container_exit

TEST_IMAGE_MAP_JSON = Path(__file__).parent / "default_images.json"


@on_init
def set_job_provider(scope):
    scope["job_provider"] = lambda id_: Job(id_, {})


async def test_workflow_to_image_map_gets_loader(loopless_main):
    @on_start(once=True)
    def check_image_map(workflow_to_docker_image):
        assert workflow_to_docker_image
        assert workflow_to_docker_image["test"]

        check_image_map.called = True

    await loopless_main(workflow_to_docker_image=TEST_IMAGE_MAP_JSON)

    assert check_image_map.called


async def test_start_container():
    client = docker.from_env()

    ubuntu = await start_workflow_container(client, {}, "ubuntu:latest")

    assert ubuntu.stats(stream=False)

    ubuntu.stop()


async def test_docker_events_trigger_on_docker_event_hook(loopless_main):
    event_triggered = asyncio.Future()
    stop_event_triggered = asyncio.Future()

    @on_docker_event(once=True)
    def check_docker_event_triggered(event):
        logging.debug(f"Docker Event: {event}")
        event_triggered.set_result(True)

    @on_docker_container_exit(once=True)
    def check_docker_on_container_exit_triggered(container):
        stop_event_triggered.set_result(True)

    @on_start(once=True)
    async def start_a_container(docker, containers):
        container = await start_workflow_container(docker, containers, "ubuntu:latest")
        container.stop()

    await loopless_main()

    assert await asyncio.wait_for(event_triggered, 100) is True
    assert await asyncio.wait_for(stop_event_triggered, 100) is True
