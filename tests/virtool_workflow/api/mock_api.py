from base64 import b64encode
from datetime import datetime
from pathlib import Path

from aiohttp import web, ContentTypeError

TEST_ANALYSIS_ID = "test_analysis"

TEST_ANALYSIS = {
    "id": TEST_ANALYSIS_ID,
    "created_at": "2017-10-03T21:35:54.813000Z",
    "job": {
        "id": "test_job"
    },
    "files": [
        {
            "analysis": "test_analysis",
            "description": None,
            "format": "fasta",
            "id": 1,
            "name": "results.fa",
            "name_on_disk": "1-results.fa",
            "size": 20466,
            "uploaded_at": "2017-10-03T21:35:54.813000Z"
        }
    ],
    "workflow": "pathoscope_bowtie",
    "sample": {
        "id": "kigvhuql",
        "name": "Test 1"
    },
    "index": {
        "id": "qldihken",
        "version": 0
    },
    "user": {
        "id": "igboyes"
    },
    "subtractions": [
        {
            "id": "yhxoynb0",
            "name": "Arabidopsis Thaliana"
        }
    ],
    "ready": False
}

mock_routes = web.RouteTableDef()

TEST_INDEX_ID = "jiwncaqr"
TEST_REF_ID = "test_ref"


@mock_routes.patch("/api/jobs/{job_id}")
async def acquire_job(request):
    json = await request.json()

    if json.get("acquired", None) is not True:
        return web.Response(status=422)

    return web.json_response({
        "task": "create_subtraction",
        "args": {
            "subtraction_id": "Thale",
            "analysis_id": "test_analysis",
            "file_id": "vlekszor-ATgenomeTAIR9.171"
        },
        "proc": 2,
        "mem": 4,
        "user": {
            "id": "igboyes"
        },
        "status": [
            {
                "state": "waiting",
                "stage": None,
                "error": None,
                "progress": 0,
                "timestamp": "2018-02-06T22:15:52.664000Z"
            },
            {
                "state": "running",
                "stage": "mk_subtraction_dir",
                "error": None,
                "progress": 0.2,
                "timestamp": "2018-02-06T22:16:11.166000Z"
            },
            {
                "state": "running",
                "stage": "set_stats",
                "error": None,
                "progress": 0.4,
                "timestamp": "2018-02-06T22:16:11.169000Z"
            },
            {
                "state": "running",
                "stage": "bowtie_build",
                "error": None,
                "progress": 0.6,
                "timestamp": "2018-02-06T22:16:15.637000Z"
            }
        ],
        "id": "zzpugkyt",
        "key": b64encode(b"test_key").decode("utf-8")
    }, status=200)


@mock_routes.get("/api/analyses/{analysis_id}")
async def get_analysis(request):
    id_ = request.match_info["analysis_id"]

    if id_ != "test_analysis":
        return web.json_response({
            "message": "Not Found"
        }, status=404)

    return web.json_response({
        "id": "test_analysis",
        "created_at": "2017-10-03T21:35:54.813000Z",
        "job": {
            "id": "test_job"
        },
        "files": [
            {
                "analysis": "test_analysis",
                "description": None,
                "format": "fasta",
                "id": 1,
                "name": "results.fa",
                "name_on_disk": "1-results.fa",
                "size": 20466,
                "uploaded_at": "2017-10-03T21:35:54.813000Z"
            }
        ],
        "workflow": "pathoscope_bowtie",
        "sample": {
            "id": "kigvhuql",
            "name": "Test 1"
        },
        "index": {
            "id": "qldihken",
            "version": 0
        },
        "user": {
            "id": "igboyes"
        },
        "subtractions": [
            {
                "id": "yhxoynb0",
                "name": "Arabidopsis Thaliana"
            }
        ],
        "ready": False
    }, status=200)


@mock_routes.post("/api/analyses/{analysis_id}/files")
async def upload_file(request):
    reader = await request.multipart()
    file = await reader.next()

    name = request.query.get("name")
    format = request.query.get("format")

    size = 0
    while True:
        chunk = await file.read_chunk(1000)
        if not chunk:
            break
        size += len(chunk)

    return web.json_response({
        "id": 1,
        "description": None,
        "name": name,
        "format": format,
        "name_on_disk": f"1-{name}",
        "size": size,
        "uploaded_at": str(datetime.now()),
    }, status=201)


@mock_routes.get("/api/indexes/{index_id}")
async def get_index(request):
    if request.match_info["index_id"] != TEST_INDEX_ID:
        return web.json_response({"message": "Not Found"}, status=404)

    return web.json_response({
        "version": 0,
        "created_at": "2018-02-01T00:28:49.798000Z",
        "manifest": {
            "c93ec9a9": 0,
        },
        "ready": False,
        "user": {
            "id": "igboyes"
        },
        "job": {
            "id": "wwssuhhy"
        },
        "id": "jiwncaqr",
        "contributors": [
            {
                "id": "igboyes",
                "count": 1419
            }
        ],
        "change_count": 1419
    }, status=200)


@mock_routes.get("/api/analyses/{analysis_id}/files/{file_id}")
async def download(request):
    file_id = request.match_info["file_id"]
    analysis_id = request.match_info["analysis_id"]

    if file_id == "0" and analysis_id == TEST_ANALYSIS_ID:
        test_file = Path("test.txt")
        test_file.write_text("TEST")
        response = web.FileResponse(test_file)

        return response

    return web.json_response({
        "message": "Not Found"
    }, status=404)


@mock_routes.delete("/api/analyses/{analysis_id}")
async def delete(request):
    analysis_id = request.match_info["analysis_id"]

    if analysis_id != TEST_ANALYSIS_ID:
        return web.json_response({
            "message": "Not Found"
        }, status=404)

    return web.Response(status=204)


@mock_routes.patch("/api/analyses/{analysis_id}")
async def upload_result(request):
    analysis_id = request.match_info["analysis_id"]
    if analysis_id != TEST_ANALYSIS_ID:
        return web.json_response({
            "message": "Not Found"
        }, status=404)

    try:
        req_json = await request.json()
        results = req_json["results"]
    except (ContentTypeError, KeyError):
        return web.json_response({
            "message": "Invalid JSON body."
        }, status=422)

    if "ready" in TEST_ANALYSIS and TEST_ANALYSIS["ready"] is True:
        return web.json_response({
            "message": "There is already a result."
        }, status=409)

    TEST_ANALYSIS.update(
        {
            "results": results,
            "ready": True
        }
    )

    return web.json_response(TEST_ANALYSIS, status=200)
