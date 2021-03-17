import os
from pathlib import Path

from virtool_workflow.analysis.read_prep.skewer import rename_trimming_results
from virtool_workflow.analysis.utils import ReadPaths
from virtool_workflow.execution.run_subprocess import RunSubprocess


class Trimming:
    def __init__(self, parameters: dict, input_paths: ReadPaths, number_of_processes: int,
                 run_subprocess: RunSubprocess):
        self.parameters = parameters
        self.input_paths = input_paths
        self.number_of_processes = number_of_processes
        self.run_subprocess = run_subprocess

    def trimming_command(self, output_path: Path):
        """Get the trimming command."""
        command = [
            "skewer",
            "-r", str(self.parameters["max_error_rate"]),
            "-d", str(self.parameters["max_indel_rate"]),
            "-m", str(self.parameters["mode"]),
            "-l", str(self.parameters["min_length"]),
            "-q", str(self.parameters["end_quality"]),
            "-Q", str(self.parameters["mean_quality"]),
            "-t", str(self.number_of_processes),
            "-o", str(output_path / "reads"),
            "-n",
            "-z",
            "--quiet",
        ]

        if self.parameters["max_length"]:
            command += [
                "-L", str(self.parameters["max_length"]),
                "-e"
            ]

        command += [str(path) for path in self.input_paths]

        return command

    async def run_trimming(self, output_path: Path):
        env = dict(os.environ, LD_LIBRARY_PATH="/usr/lib/x86_64-linux-gnu")
        await self.run_subprocess(self.trimming_command(output_path), env=env)
        rename_trimming_results(output_path)
        return output_path
