from base64 import b64encode
from datetime import datetime

from aiohttp import web
from aiohttp.web_response import json_response

mock_routes = web.RouteTableDef()

TEST_JOB = {
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
}


@mock_routes.patch("/api/jobs/{job_id}")
async def acquire_job(request):
    json = await request.json()

    if json.get("acquired") is not True:
        return web.Response(status=422)

    return web.json_response(TEST_JOB, status=200)


@mock_routes.post("/api/jobs/{job_id}/status")
async def push_status(request):
    job_id = request.match_info["job_id"]

    if job_id != TEST_JOB["id"]:
        return json_response({
            "message": "Not Found",
        }, status=404)

    status = await request.json()

    TEST_JOB["status"].append({k: v for k, v in status.items() if k in [
        "error", "progress", "stage", "state",
    ]})

    return web.json_response({
        **status,
        "timestamp": datetime.now().isoformat()},
    )
