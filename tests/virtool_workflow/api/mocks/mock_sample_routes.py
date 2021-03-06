import json
from pathlib import Path

from aiohttp.web_routedef import RouteTableDef

from virtool.api.response import not_found, json_response

mock_routes = RouteTableDef()

TEST_SAMPLE_PATH = Path(__file__).parent / "mock_sample.json"
TEST_SAMPLE = json.load(TEST_SAMPLE_PATH)
TEST_SAMPLE_ID = TEST_SAMPLE["id"]


@mock_routes.get("/api/samples/{sample_id}")
async def get_sample(request):
    sample_id = request.match_info["sample_id"]

    if sample_id != TEST_SAMPLE_ID:
        return not_found()

    return json_response(TEST_SAMPLE, status=200)
