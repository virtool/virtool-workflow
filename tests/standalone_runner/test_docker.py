from pathlib import Path

from virtool_workflow_runtime.hooks import on_start

TEST_IMAGE_MAP_JSON = Path(__file__).parent / "default_images.json"


async def test_workflow_to_image_map_gets_loader(loopless_main):
    @on_start(once=True)
    def check_image_map(workflow_to_docker_image):
        assert workflow_to_docker_image
        assert workflow_to_docker_image["test"]

        check_image_map.called = True

    await loopless_main(workflow_to_docker_image=TEST_IMAGE_MAP_JSON)

    assert check_image_map.called
