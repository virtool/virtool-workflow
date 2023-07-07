import tempfile
from datetime import datetime
from pathlib import Path

from aiohttp import web

from tests.conftest import ANALYSIS_TEST_FILES_DIR

mock_routes = web.RouteTableDef()

TEST_INDEX_ID = "jiwncaqr"
TEST_REF_ID = "21n3j5v6"

TEST_REF = {
    "id": "21n3j5v6",
    "created_at": "2019-10-04T17:17:48.935Z",
    "data_type": "genome",
    "description": "",
    "name": "Clone of Banana Viruses",
    "organism": "virus",
    "internal_control": None,
    "restrict_source_types": False,
    "source_types": ["isolate", "strain"],
    "groups": [],
    "cloned_from": {"id": "9mciizg6", "name": "Banana Viruses"},
    "process": {"id": "zhio57ug"},
    "otu_count": 42,
    "unbuilt_change_count": 12,
    "user": {"id": "test", "handle": "test", "administrator": False},
}

TEST_INDEX = {
    "id": TEST_INDEX_ID,
    "change_count": 1419,
    "contributors": [
        {"administrator": False, "count": 478, "handle": "jasper", "id": "1kg24j7t"},
        {"administrator": True, "count": 162, "handle": "mrott", "id": "ihvze2u9"},
    ],
    "created_at": "2018-02-01T00:28:49.798000Z",
    "files": [],
    "has_files": False,
    "job": None,
    "manifest": {
        "c93ec9a9": 0,
    },
    "modified_otu_count": 4,
    "ready": False,
    "reference": TEST_REF,
    "user": {"id": "abc12345", "handle": "igboyes", "administrator": False},
    "otus": [
        {"change_count": 4, "id": "d1efjvxk", "name": "Agaricus bisporus virus 1"},
        {
            "change_count": 6,
            "id": "u9vbhtg1",
            "name": "Alternaria solani chrysovirus 1",
        },
        {
            "change_count": 5,
            "id": "af3xznax",
            "name": "Alternaria tenuissima partitivirus 1",
        },
    ],
    "version": 0,
}


@mock_routes.get("/indexes/{index_id}")
async def get_index(request):
    if request.match_info["index_id"] != TEST_INDEX_ID:
        return web.json_response({"message": "Not Found"}, status=404)

    return web.json_response(TEST_INDEX, status=200)


@mock_routes.get("/refs/{ref_id}")
async def get_ref(request):
    ref_id = request.match_info["ref_id"]

    if ref_id != TEST_REF_ID:
        return web.json_response({"message": "Not Found"}, status=404)

    return web.json_response(TEST_REF, status=200)


@mock_routes.put("/indexes/{index_id}/files/{name}")
async def upload_index_file(request):
    name = request.match_info.get("name")

    reader = await request.multipart()
    file = await reader.next()

    size = 0
    while True:
        chunk = await file.read_chunk(1000)
        if not chunk:
            break
        size += len(chunk)

    return web.json_response(
        {
            "id": 1,
            "description": None,
            "name": name,
            "format": "fasta",
            "name_on_disk": f"1-{name}",
            "size": size,
            "uploaded_at": str(datetime.now()),
        },
        status=201,
    )


@mock_routes.get("/indexes/{index_id}/files/{filename}")
async def download_index_files(request):
    index_id = request.match_info["index_id"]
    filename = request.match_info["filename"]

    if filename in (
        "reference.fa.gz",
        "reference.1.bt2",
        "reference.2.bt2",
        "reference.3.bt2",
        "reference.4.bt2",
        "reference.rev.1.bt2",
        "reference.rev.2.bt2",
    ):
        path = Path(tempfile.mkstemp()[1])
    else:
        path = ANALYSIS_TEST_FILES_DIR / filename

    if index_id != TEST_INDEX_ID or not path.exists():
        return web.json_response({"message": "Not Found"}, status=404)

    return web.FileResponse(
        path,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Type": "application/octet-stream",
        },
    )


@mock_routes.patch("/indexes/{index_id}")
async def finalize_index(request):
    TEST_INDEX["ready"] = True

    return web.json_response(TEST_INDEX, status=200)
