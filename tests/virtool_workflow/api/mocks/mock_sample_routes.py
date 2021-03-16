import json
import tempfile
from pathlib import Path

from aiohttp.web import RouteTableDef
from aiohttp.web_fileresponse import FileResponse
from aiohttp.web_response import json_response, Response

from tests.virtool_workflow.api.mocks.utils import not_found, read_file_from_request

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

    if "ready" in TEST_SAMPLE and TEST_SAMPLE["ready"] is True:
        return json_response(
            {"message": "Already Finalized"},
            status=400,
        )

    return Response(status=204)


@mock_routes.post("/api/samples/{sample_id}/artifacts")
@mock_routes.post("/api/samples/{sample_id}/reads")
async def upload_read_files(request):
    sample_id = request.match_info["sample_id"]

    if sample_id != TEST_SAMPLE_ID:
        return not_found()

    name = request.query.get("name")
    type = request.query.get("type")

    file = await read_file_from_request(request, name, type)

    return json_response(file, status=201)


@mock_routes.get("/api/samples/{sample_id}/reads/1")
async def download_reads_file(request):
    sample_id = request.match_info["sample_id"]

    if sample_id != TEST_SAMPLE_ID:
        return not_found()

    tempdir = Path(tempfile.mkdtemp())

    reads_1 = tempdir / "reads_1.fq.gz"
    reads_1.touch()

    return FileResponse(reads_1)


@mock_routes.get("/api/samples/{sample_id}/artifacts/{filename}")
async def download_artifact(request):
    sample_id = request.match_info["sample_id"]
    filename = request.match_info["filename"]

    if sample_id != TEST_SAMPLE_ID:
        return not_found()

    tempdir = Path(tempfile.mkdtemp())

    file = tempdir / filename
    file.touch()

    return FileResponse(file)
