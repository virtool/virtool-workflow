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

TEST_CACHE = {
    "id": "test_cache",
    "created_at": None,
    "files": list(),
    "key": "test_cache",
    "legacy": False,
    "missing": False,
    "paired": TEST_SAMPLE["paired"],
    "ready": False,
    "sample": {
        "id": TEST_SAMPLE_ID
    }
}

ANALYSIS_TEST_FILES_DIR = Path(__file__).parent.parent.parent / "analysis"


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
    n = request.match_info["n"]

    if sample_id != TEST_SAMPLE_ID or n not in ("1", "2"):
        return not_found()

    file_name = "paired_small_1.fq.gz" if n == "1" else "paired_small_2.fq.gz"

    return FileResponse(ANALYSIS_TEST_FILES_DIR / file_name)


@mock_routes.get("/api/samples/{sample_id}/caches/{key}/artifacts/{filename}")
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


@mock_routes.post("/api/samples/{sample_id}/caches")
async def create_mock_cache(request):
    sample_id = request.match_info["sample_id"]

    if sample_id != TEST_SAMPLE_ID:
        return not_found()

    _json = await request.json()
    key = _json["key"]

    if key == TEST_CACHE["key"]:
        return json_response(TEST_CACHE, status=201)
    else:
        return not_found()


@mock_routes.post("/api/samples/{sample_id}/caches/{key}/artifacts")
async def upload_artifact_to_cache(request):
    sample_id = request.match_info["sample_id"]
    key = request.match_info["key"]
    type = request.query.get("type")
    name = request.query.get("name")

    if sample_id != TEST_SAMPLE_ID or key != TEST_CACHE["key"]:
        return not_found()

    document = await read_file_from_request(request, name, type)

    return json_response(document, status=201)


@mock_routes.put("/api/samples/{sample_id}/caches/{key}/reads/{name}")
async def upload_reads_to_cache(request):
    name = request.match_info["name"]
    sample_id = request.match_info["sample_id"]
    key = request.match_info["key"]

    if name not in ["reads_1.fq.gz", "reads_2.fq.gz"]:
        return not_found()

    if sample_id != TEST_SAMPLE_ID or key != TEST_CACHE["key"]:
        return not_found()

    document = await read_file_from_request(request, name, "fastq")
    return json_response(document, status=201)


@mock_routes.patch("/api/samples/{sample_id}/caches/{key}")
async def finalize_cache(request):
    sample_id = request.match_info["sample_id"]
    key = request.match_info["key"]

    if sample_id != TEST_SAMPLE_ID or key != TEST_CACHE["key"]:
        return not_found()

    _json = await request.json()

    quality = _json["quality"]
    TEST_CACHE["quality"] = quality
    TEST_CACHE["ready"] = True

    return json_response(TEST_CACHE)


@mock_routes.get("/api/samples/{sample_id}/caches/{key}")
async def get_cache(request):
    sample_id = request.match_info["sample_id"]
    key = request.match_info["key"]

    if sample_id != TEST_SAMPLE_ID or key != TEST_CACHE["key"]:
        return not_found()

    return json_response(TEST_CACHE)


@mock_routes.delete("/api/samples/{sample_id}/caches/{key}")
async def delete_cache(request):
    sample_id = request.match_info["sample_id"]
    key = request.match_info["key"]

    if sample_id != TEST_SAMPLE_ID or key != TEST_CACHE["key"]:
        return not_found()

    if TEST_CACHE["ready"] is True:
        return json_response({"message": "Cache is finalized."}, status=409)

    del TEST_CACHE

    return Response(status=204)


@mock_routes.get("/api/samples/{sample_id}/caches/{key}/reads/{name}")
async def download_cached_reads(request):
    name = request.match_info["name"]

    tmpdir = Path(tempfile.mkdtemp())

    file = (tmpdir / name)
    file.touch()

    return FileResponse(file)
