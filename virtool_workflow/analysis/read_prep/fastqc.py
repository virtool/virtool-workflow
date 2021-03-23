from virtool_workflow.analysis.fastqc import parse_fastqc
from virtool_workflow.analysis.utils import ReadPaths


def fastqc(work_path, run_subprocess):
    fastqc_path = work_path / "fastqc"
    output_path = work_path / "fastqc_out"
    fastqc_path.mkdir()
    output_path.mkdir()

    async def run_fastqc(input_paths: ReadPaths):
        """Run fastqc on the input path and return the parsed result."""
        command = [
            "fastqc",
            "-f", "fastq",
            "-o", str(fastqc_path),
            "--extract",
            *[str(path) for path in input_paths]
        ]

        await run_subprocess(command)

        return parse_fastqc(fastqc_path, output_path)

    run_fastqc.output_path = output_path

    return run_fastqc
