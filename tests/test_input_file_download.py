from virtool_workflow.api.uploads import input_files
from pathlib import Path


async def test_input_files_fixture(tmpdir):

    async def mock_download(id, target):
        return target

    files = await input_files(
        files_list=[
            {
                "id": "1",
                "name": "file1.txt",
            },
            {
                "id": "2",
                "name": "file2.txt",
            }
        ],
        download_input_file=mock_download,
        work_path=tmpdir,
    )


    assert files["file1.txt"] == Path(tmpdir/"files/file1.txt")
    assert files["file2.txt"] == Path(tmpdir/"files/file2.txt")
