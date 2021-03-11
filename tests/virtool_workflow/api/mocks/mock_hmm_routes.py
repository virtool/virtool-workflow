import json
from pathlib import Path

from aiohttp.web_fileresponse import FileResponse
from aiohttp.web_response import json_response
from aiohttp.web_routedef import RouteTableDef

mock_routes = RouteTableDef()

MOCK_HMM = {
    "families": {
        "None": 1,
        "Geminiviridae": 203
    },
    "total_entropy": 72.08,
    "length": 136,
    "cluster": 3,
    "entries": [
        {
            "accession": "NP_040323.1",
            "gi": "9626084",
            "organism": "Pepper huasteco yellow vein virus",
            "name": "AL2 protein"
        },
        {
            "accession": "NP_044924.1",
            "gi": "9629639",
            "organism": "Tomato mottle Taino virus",
            "name": "transactivator protein"
        }
    ],
    "genera": {
        "Begomovirus": 197,
        "Topocuvirus": 1,
        "None": 2,
        "Curtovirus": 4
    },
    "mean_entropy": 0.53,
    "count": 216,
    "names": ["AC2 protein", "C2 protein", "AC2"],
    "hidden": False,
    "id": "zltnktou"
}

HMM_PROFILES = Path(__file__).parent.parent / "files/profiles.hmm"


@mock_routes.get("/api/hmm/{hmm_id}")
async def get(request):
    hmm_id = request.match_info["hmm_id"]

    if hmm_id != MOCK_HMM["id"]:
        return json_response({
            "message": "Not Found"
        }, status=404)

    return json_response(MOCK_HMM)


@mock_routes.get('/download/hmms/profiles.hmm')
async def download_hmm_profiles(request):
    return FileResponse(HMM_PROFILES)


@mock_routes.get('/api/hmm/files/annotations.json.gz')
async def download_annotations(request):
    annotations_path = Path("annotations.json.gz")

    with annotations_path.open("w") as f:
        json.dump([MOCK_HMM] * 10, f)

    return FileResponse(annotations_path)
