from datetime import datetime
from pathlib import Path

from aiohttp import web

mock_routes = web.RouteTableDef()

TEST_INDEX_ID = "jiwncaqr"
TEST_REF_ID = "21n3j5v6"


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


@mock_routes.get("/api/refs/{ref_id}")
async def get_ref(request):
    ref_id = request.match_info["ref_id"]

    if ref_id != TEST_REF_ID:
        return web.json_response({"message": "Not Found"}, status=404)

    return web.json_response({
        "id": "21n3j5v6",
        "created_at": {
            "$date": "2019-10-04T17:17:48.935Z"
        },
        "data_type": "genome",
        "description": "",
        "name": "Clone of Banana Viruses",
        "organism": "virus",
        "internal_control": None,
        "restrict_source_types": False,
        "source_types": [
            "isolate",
            "strain"
        ],
        "groups": [

        ],
        "cloned_from": {
            "id": "9mciizg6",
            "name": "Banana Viruses"
        },
        "process": {
            "id": "zhio57ug"
        }
    }, status=200)


@mock_routes.post("/api/indexes/{index_id}/files")
async def upload_index_file(request):
    print(request.content_type)
    reader = await request.multipart()
    file = await reader.next()

    name = request.query.get("name")

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
        "format": "fasta",
        "name_on_disk": f"1-{name}",
        "size": size,
        "uploaded_at": str(datetime.now()),
    }, status=201)


@mock_routes.get("/api/indexes/{index_id}/files/{filename}")
def download_index_files(request):
    index_id = request.match_info["index_id"]
    filename = request.match_info["filename"]

    if index_id != TEST_INDEX_ID or filename != "reference.json.gz":
        return web.json_response({
            "message": "Not Found"
        }, status=404)

    return web.FileResponse(Path(__file__).parent / "files/reference.json.gz")
