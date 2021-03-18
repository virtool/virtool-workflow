from virtool_workflow.analysis.fastqc import parse_fastqc
from virtool_workflow.analysis.utils import ReadPaths


def fastqc(work_path, run_subprocess):
    fastqc_path = work_path / "fastqc"
    fastqc_path.mkdir()

    async def run_fastqc(self, input_paths: ReadPaths):
        """Run fastqc on the input path and return the parsed result."""
        command = [
            "fastqc",
            "-f", "fastq",
            "-o", str(fastqc_path),
            "--extract",
            *[str(path) for path in input_paths]
        ]

        await run_subprocess(command)

        return parse_fastqc(self.path, self.path)

    return run_fastqc
