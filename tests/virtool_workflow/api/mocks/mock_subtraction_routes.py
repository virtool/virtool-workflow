from aiohttp import web

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
