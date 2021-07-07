from aiohttp import web

from tests.api.mocks.utils import read_file_from_request

mock_routes = web.RouteTableDef()

TEST_SUBTRACTION_ID = "Apis mellifera"

TEST_SUBTRACTION = {
    "id": TEST_SUBTRACTION_ID,
    "nickname": "honey bee",
    "ready": True,
    "is_host": True,
    "file": {
        "id": "ii23chjh-GCF_003254395.2_Amel_HAv3.1_genomic.fa",
        "name": "GCF_003254395.2_Amel_HAv3.1_genomic.fa"
    },
    "user": {
        "id": "james"
    },
    "job": {
        "id": "98b12fh9"
    },
    "count": 177,
    "gc": {
        "a": 0.336,
        "t": 0.335,
        "g": 0.162,
        "c": 0.162,
        "n": 0.006
    },
    "name": "Apis mellifera",
    "deleted": True
}


@mock_routes.get("/api/subtractions/{subtraction_id}")
def get_subtraction(request):
    subtraction_id = request.match_info["subtraction_id"]

    if subtraction_id != TEST_SUBTRACTION_ID:
        return web.json_response({
            "message": "Not Found"
        }, status=404)

    return web.json_response(TEST_SUBTRACTION, status=200)


@mock_routes.put("/api/subtractions/{subtraction_id}/files")
async def upload_subtraction_file(request):
    name = request.query.get("name")

    if name not in [
        "subtraction.fa.gz",
        "subtraction.1.bt2",
        "subtraction.2.bt2",
        "subtraction.3.bt2",
        "subtraction.4.bt2",
        "subtraction.rev.1.bt2",
        "subtraction.rev.2.bt2"
    ]:
        return web.json_response({
            "message": "Unsupported file name."
        }, status=400)

    return web.json_response(await read_file_from_request(request, name, "bt2"), status=201)


@mock_routes.patch("/api/subtractions/{subtraction_id}")
async def finalize_subtraction(request):
    subtraction_id = request.match_info["subtraction_id"]

    if subtraction_id != TEST_SUBTRACTION_ID:
        return web.json_response({"message": "Not Found"}, status=404)

    request_json = await request.json()

    TEST_SUBTRACTION["ready"] = True
    TEST_SUBTRACTION["gc"] = request_json["gc"]

    return web.json_response(TEST_SUBTRACTION)


@mock_routes.delete("/api/subtractions/{subtraction_id}")
async def delete_subtraction(request):
    subtraction_id = request.match_info["subtraction_id"]

    if subtraction_id != TEST_SUBTRACTION_ID:
        return web.json_response({"message": "Not Found"}, status=404)

    if "ready" in TEST_SUBTRACTION and TEST_SUBTRACTION["ready"] is True:
        return web.json_response({"message": "Conflict"}, status=409)

    return web.Response(status=204)


@mock_routes.get("/api/subtractions/{subtraction_id}/files/{filename}")
async def download_subtraction_data(request):
    return web.Response(status=200)
