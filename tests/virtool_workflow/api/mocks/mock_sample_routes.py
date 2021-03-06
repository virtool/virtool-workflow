import json
from pathlib import Path

from aiohttp.web import RouteTableDef
from aiohttp.web_response import json_response, Response

from tests.virtool_workflow.api.mocks.utils import not_found

mock_routes = RouteTableDef()

TEST_SAMPLE_PATH = Path(__file__).parent / "mock_sample.json"
with TEST_SAMPLE_PATH.open('r') as f:
    TEST_SAMPLE = json.load(f)
TEST_SAMPLE_ID = TEST_SAMPLE["id"]


@mock_routes.get("/api/samples/{sample_id}")
async def get_sample(request):
    sample_id = request.match_info["sample_id"]

    if sample_id != TEST_SAMPLE_ID:
        return not_found()

    return json_response(TEST_SAMPLE, status=200)


@mock_routes.patch("/api/samples/{sample_id}")
async def finalize(request):
    sample_id = request.match_info["sample_id"]

    if sample_id != TEST_SAMPLE_ID:
        return not_found()

    response_json = await request.json()

    TEST_SAMPLE["quality"] = response_json["quality"]
    TEST_SAMPLE["ready"] = True

    return json_response(TEST_SAMPLE)


@mock_routes.delete("/api/samples/{sample_id}")
async def delete(request):
    sample_id = request.match_info["sample_id"]

    if sample_id != TEST_SAMPLE_ID:
        return not_found()

    return Response(status=201)
