import json
import tempfile
from pathlib import Path

from aiohttp.web import RouteTableDef
from aiohttp.web_fileresponse import FileResponse
from aiohttp.web_response import json_response, Response

from tests.conftest import ANALYSIS_TEST_FILES_DIR
from tests.api.mocks.utils import not_found, read_file_from_request

mock_routes = RouteTableDef()

TEST_SAMPLE_PATH = Path(__file__).parent / "mock_sample.json"
with TEST_SAMPLE_PATH.open('r') as f:
    TEST_SAMPLE = json.load(f)
TEST_SAMPLE_ID = TEST_SAMPLE["id"]


@mock_routes.get("/samples/{sample_id}")
async def get_sample(request):
    sample_id = request.match_info["sample_id"]

    if sample_id != TEST_SAMPLE_ID:
        return not_found()

    return json_response(TEST_SAMPLE, status=200)


@mock_routes.patch("/samples/{sample_id}")
async def finalize(request):
    sample_id = request.match_info["sample_id"]

    if sample_id != TEST_SAMPLE_ID:
        return not_found()

    response_json = await request.json()

    TEST_SAMPLE["quality"] = response_json["quality"]
    TEST_SAMPLE["ready"] = True

    return json_response(TEST_SAMPLE)


@mock_routes.delete("/samples/{sample_id}")
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


@mock_routes.put("/samples/{sample_id}/artifacts")
async def upload_artifact_files(request):
    sample_id = request.match_info["sample_id"]

    if sample_id != TEST_SAMPLE_ID:
        return not_found()

    name = request.query.get("name")
    type = request.query.get("type")

    file = await read_file_from_request(request, name, type)

    return json_response(file, status=201)


@mock_routes.put("/samples/{sample_id}/reads/{name}")
async def upload_read_files(request):
    sample_id = request.match_info["sample_id"]
    name = request.match_info["name"]

    if sample_id != TEST_SAMPLE_ID:
        return not_found()

    file = await read_file_from_request(request, name, "fastq")

    return json_response(file, status=201)


@mock_routes.get("/samples/{sample_id}/reads/{filename}")
async def download_reads_file(request):
    sample_id = request.match_info["sample_id"]
    filename = request.match_info["filename"]

    if sample_id != TEST_SAMPLE_ID or filename not in ("reads_1.fq.gz", "reads_2.fq.gz"):
        return not_found()

    file_name = "paired_small_1.fq.gz" if filename == "reads_1.fq.gz" else "paired_small_2.fq.gz"

    return FileResponse(ANALYSIS_TEST_FILES_DIR / file_name, headers={
        "Content-Disposition": f"attachment; filename={file_name}",
        "Content-Type": "application/octet-stream"
    })


@mock_routes.get("/samples/{sample_id}/artifacts/{filename}")
async def download_artifact(request):
    sample_id = request.match_info["sample_id"]
    filename = request.match_info["filename"]

    if sample_id != TEST_SAMPLE_ID:
        return not_found()

    tempdir = Path(tempfile.mkdtemp())

    file = tempdir / filename
    file.touch()

    return FileResponse(file)


