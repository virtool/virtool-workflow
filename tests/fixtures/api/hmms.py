from pathlib import Path

from aiohttp.web import FileResponse, RouteTableDef, View

from tests.fixtures.api.utils import generate_not_found
from tests.fixtures.data import Data


def create_hmms_routes(data: Data, example_path: Path):
    routes = RouteTableDef()

    @routes.view("/hmms/files/{file_name}")
    class HMMFilesView(View):
        async def get(self):
            file_name = self.request.match_info["file_name"]

            if file_name == "profiles.hmm":
                return FileResponse(
                    example_path / "hmms" / "profiles.hmm",
                    headers={
                        "Content-Disposition": "attachment; filename='profiles.hmm'",
                        "Content-Type": "application/octet-stream",
                    },
                )

            if file_name == "annotations.json.gz":
                return FileResponse(
                    example_path / "hmms" / "annotations.json.gz",
                    headers={
                        "Content-Disposition": "attachment; filename='annotations.json.gz'",
                        "Content-Type": "application/octet-stream",
                    },
                )

            return generate_not_found()

    return routes
