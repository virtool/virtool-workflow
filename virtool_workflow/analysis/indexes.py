import asyncio
from pathlib import Path
from typing import List

from pyfixtures import fixture

from virtool_workflow.api.indexes import IndexProvider
from virtool_workflow.data_model.indexes import WFIndex
from virtool_workflow.runtime.run_subprocess import RunSubprocess


@fixture
async def indexes(
    index_provider: IndexProvider,
    work_path: Path,
    run_subprocess: RunSubprocess,
) -> List[WFIndex]:
    """A workflow fixture that lists all reference indexes required for the workflow as :class:`.Index` objects."""
    index_ = await index_provider.get()

    index_work_path = work_path / "indexes" / index_.id

    await asyncio.to_thread(index_work_path.mkdir, parents=True, exist_ok=True)

    if index_.ready:
        await index_provider.download(index_work_path)
    else:
        await index_provider.download(index_work_path, "otus.json.gz")

    index = WFIndex(
        index_,
        index_work_path,
        index_provider.finalize,
        index_provider.upload,
        run_subprocess,
    )

    await index.decompress_json()

    return [index]
