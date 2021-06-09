import click
from pathlib import Path
from subprocess import call
from dotenv import dotenv_values

root_dir = Path(__file__).parent


@click.command()
def run_integration():
    test_cases = (dir_ for dir_ in root_dir.iterdir() if dir_.is_dir())
    for test_case_dir in test_cases:
        env = dotenv_values(test_case_dir/".env")

        cmd = [
            "workflow",
            "test",
            *(arg for arg in env["VT_ADD_ARGS"].split(" ") if arg),
            env["VT_JOB_ID"]
        ]

        call(cmd, cwd=test_case_dir)


if __name__ == "__main__":
    run_integration()
