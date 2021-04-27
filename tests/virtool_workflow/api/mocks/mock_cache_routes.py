import tempfile
from pathlib import Path

from aiohttp.web_routedef import RouteTableDef

cache_path = Path(tempfile.mkdtemp())
caches = {}

mock_routes = RouteTableDef()


@mock_routes.post("/api/caches/{key}")
def create_cache_placeholder(request):
    raise NotImplementedError()


@mock_routes.post("/api/caches/{key}/files")
def upload_cache_file(request):
    raise NotImplementedError()


@mock_routes.get("/api/caches/{key}")
def get_cache(request):
    raise NotImplementedError()


@mock_routes.patch("/api/caches/{key}")
def finalize(request):
    raise NotImplementedError()
