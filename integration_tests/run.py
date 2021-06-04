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

        out, err = proc.communicate()

        print(out)
        print(err)

        if proc.returncode != 0:
            raise RuntimeError(
                f"{test_case_dir} exited with error code {return_code}")


if __name__ == "__main__":
    run_integration()
