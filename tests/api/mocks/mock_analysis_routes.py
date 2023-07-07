from aiohttp import web, ContentTypeError

from tests.api.mocks.utils import read_file_from_request
from tests.conftest import TEST_FILES_DIR

mock_routes = web.RouteTableDef()


@mock_routes.get("/analyses/{analysis_id}")
async def get_analysis(request):
    id_ = request.match_info["analysis_id"]

    if id_ != "test_analysis":
        return web.json_response({"message": "Not Found"}, status=404)

    return web.json_response(
        {
            "id": "test_analysis",
            "created_at": "2017-10-03T21:35:54.813000Z",
            "files": [
                {
                    "analysis": "test_analysis",
                    "description": None,
                    "format": "fasta",
                    "id": 1,
                    "name": "results.fa",
                    "name_on_disk": "1-results.fa",
                    "size": 20466,
                    "uploaded_at": "2017-10-03T21:35:54.813000Z",
                }
            ],
            "index": {"id": "qldihken", "version": 0},
            "job": None,
            "ready": False,
            "reference": {"id": "foo", "name": "Foo", "data_type": "genome"},
            "sample": {"id": "kigvhuql", "name": "Test 1"},
            "subtractions": [{"id": "yhxoynb0", "name": "Arabidopsis Thaliana"}],
            "user": {"id": "abc12345", "handle": "igboyes", "administrator": False},
            "workflow": "pathoscope_bowtie",
        },
        status=200,
    )


@mock_routes.put("/analyses/{analysis_id}/files")
async def upload_file(request):
    return web.json_response(
        await read_file_from_request(
            request, request.query.get("name"), request.query.get("format")
        ),
        status=201,
    )


@mock_routes.get("/analyses/{analysis_id}/files/{file_id}")
async def download(request):
    file_id = request.match_info["file_id"]
    analysis_id = request.match_info["analysis_id"]

    if file_id == "0" and analysis_id == TEST_ANALYSIS_ID:
        test_file = TEST_FILES_DIR / "blank.txt"

        response = web.FileResponse(test_file)

        return response

    return web.json_response({"message": "Not Found"}, status=404)


@mock_routes.delete("/analyses/{analysis_id}")
async def delete(request):
    analysis_id = request.match_info["analysis_id"]

    if analysis_id != TEST_ANALYSIS_ID:
        return web.json_response({"message": "Not Found"}, status=404)

    return web.Response(status=204)


@mock_routes.patch("/analyses/{analysis_id}")
async def upload_result(request):
    analysis_id = request.match_info["analysis_id"]

    if analysis_id != TEST_ANALYSIS_ID:
        return web.json_response({"message": "Not Found"}, status=404)

    try:
        req_json = await request.json()
        results = req_json["results"]
    except (ContentTypeError, KeyError):
        return web.json_response({"message": "Invalid JSON body."}, status=422)

    return web.json_response({**TEST_ANALYSIS, "results": results}, status=200)


TEST_ANALYSIS_ID = "test_analysis"
TEST_ANALYSIS = {
    "id": TEST_ANALYSIS_ID,
    "created_at": "2017-10-03T21:35:54.813000Z",
    "job": None,
    "files": [
        {
            "analysis": "test_analysis",
            "description": None,
            "format": "fasta",
            "id": 1,
            "name": "results.fa",
            "name_on_disk": "1-results.fa",
            "size": 20466,
            "uploaded_at": "2017-10-03T21:35:54.813000Z",
        }
    ],
    "workflow": "pathoscope_bowtie",
    "sample": {"id": "kigvhuql", "name": "Test 1"},
    "index": {"id": "qldihken", "version": 0},
    "user": {"id": "abc12345", "handle": "igboyes", "administrator": False},
    "subtractions": [{"id": "yhxoynb0", "name": "Arabidopsis Thaliana"}],
    "ready": False,
    "reference": {"id": "foo", "name": "Foo", "data_type": "genome"},
}
