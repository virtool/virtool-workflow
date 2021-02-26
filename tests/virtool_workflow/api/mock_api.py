from base64 import b64encode

from aiohttp import web

mock_routes = web.RouteTableDef()


@mock_routes.patch("/api/jobs/{job_id}")
async def acquire_job(request):
    json = await request.json()

    if json.get("acquired", None) is not True:
        return web.Response(status=422)

    return web.json_response({
        "task": "create_subtraction",
        "args": {
            "subtraction_id": "Thale",
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
