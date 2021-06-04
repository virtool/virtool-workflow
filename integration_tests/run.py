import click
from pathlib import Path
from subprocess import Popen, PIPE

root_dir = Path(__file__).parent


@click.command()
def run_integration():
    test_cases = (dir_ for dir_ in root_dir.iterdir() if dir_.is_dir())
    for test_case_dir in test_cases:
        print(f"Running test case {test_case_dir}")
        proc = Popen(
            [
                "docker-compose",
                "up",
                "--build",
                "--abort-on-container-exit",
                "--force-recreate",
                "--exit-code-from",
                "workflow"
            ],
            cwd=test_case_dir,
            stdout=PIPE,
            stderr=PIPE,
        )

        for line in (str(line, encoding="utf-8") for line in proc.stdout):
            print(line.strip())

        for line in (str(line, encoding="utf-8") for line in proc.stderr):
            print(line.strip())

        if proc.returncode != 0:
            raise RuntimeError(
                f"{test_case_dir} exited with error code {proc.returncode}")


if __name__ == "__main__":
    run_integration()
