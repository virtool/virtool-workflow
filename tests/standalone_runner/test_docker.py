import docker
from pathlib import Path

from virtool_workflow_runtime._docker import start_workflow_container
from virtool_workflow_runtime.hooks import on_start, on_init

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

    ubuntu = await start_workflow_container(client, "ubuntu:latest")

    assert ubuntu.stats(stream=False)

    ubuntu.stop()


async def test_docker_events_trigger_on_docker_event_hook(loopless_main):
    await loopless_main
