import arrow
from aiohttp import web

from tests.api.mocks.utils import read_file_from_request

mock_routes = web.RouteTableDef()

TEST_SUBTRACTION_ID = "Apis mellifera"

TEST_SUBTRACTION = {
    "id": TEST_SUBTRACTION_ID,
    "created_at": arrow.utcnow().isoformat(),
    "deleted": False,
    "file": {
        "id": 642,
        "name": "Apis_mellifera.Amel_HAv3.1.dna.toplevel.fa.gz",
    },
    "files": [],
    "linked_samples": [],
    "nickname": "Honey Bee",
    "ready": True,
    "user": {"id": "abc12345", "handle": "james", "administrator": False},
    "job": None,
    "count": 33,
    "gc": {"a": 0.336, "t": 0.335, "g": 0.162, "c": 0.162, "n": 0.006},
    "name": "Apis mellifera",
}


@mock_routes.get("/subtractions/{subtraction_id}")
def get_subtraction(request):
    subtraction_id = request.match_info["subtraction_id"]

    if subtraction_id != TEST_SUBTRACTION_ID:
        return web.json_response({"message": "Not Found"}, status=404)

    return web.json_response(TEST_SUBTRACTION, status=200)


@mock_routes.put("/subtractions/{subtraction_id}/files/{filename}")
async def upload_subtraction_file(request):
    name = request.match_info["filename"]

    if name not in [
        "subtraction.fa.gz",
        "subtraction.1.bt2",
        "subtraction.2.bt2",
        "subtraction.3.bt2",
        "subtraction.4.bt2",
        "subtraction.rev.1.bt2",
        "subtraction.rev.2.bt2",
    ]:
        return web.json_response({"message": "Unsupported file name."}, status=400)

    return web.json_response(
        await read_file_from_request(request, name, "bt2"), status=201
    )


@mock_routes.patch("/subtractions/{subtraction_id}")
async def finalize_subtraction(request):
    subtraction_id = request.match_info["subtraction_id"]

    if subtraction_id != TEST_SUBTRACTION_ID:
        return web.json_response({"message": "Not Found"}, status=404)

    request_json = await request.json()

    TEST_SUBTRACTION["ready"] = True
    TEST_SUBTRACTION["gc"] = request_json["gc"]
    TEST_SUBTRACTION["count"] = request_json["count"]

    return web.json_response(TEST_SUBTRACTION)


@mock_routes.delete("/subtractions/{subtraction_id}")
async def delete_subtraction(request):
    subtraction_id = request.match_info["subtraction_id"]

    if subtraction_id != TEST_SUBTRACTION_ID:
        return web.json_response({"message": "Not Found"}, status=404)

    if "ready" in TEST_SUBTRACTION and TEST_SUBTRACTION["ready"] is True:
        return web.json_response({"message": "Conflict"}, status=409)

    return web.Response(status=204)


@mock_routes.get("/subtractions/{subtraction_id}/files/{filename}")
async def download_subtraction_data(request):
    return web.Response(status=200)
