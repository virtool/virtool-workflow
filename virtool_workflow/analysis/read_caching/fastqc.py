from virtool_workflow.analysis.fastqc import parse_fastqc
from virtool_workflow.analysis.utils import ReadPaths


class FastQC:
    def __init__(self, work_path, run_subprocess):
        self.work_path = work_path
        self.path = work_path / "fastqc"
        self.path.mkdir()

        self.run_subprocess = run_subprocess

    async def run(self, input_paths: ReadPaths):
        """Run fastqc on the input path and return the parsed result."""
        command = [
            "fastqc",
            "-f", "fastq",
            "-o", str(self.path),
            "--extract",
            *[str(path) for path in input_paths]
        ]

        await self.run_subprocess(command)

        return parse_fastqc(self.path, self.path)
