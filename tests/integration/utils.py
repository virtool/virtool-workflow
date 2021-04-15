import os
from shutil import which
from subprocess import call


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def color(color, text):
    return f"{color}{text}{bcolors.ENDC}"


DONE = color(bcolors.OKGREEN, color(bcolors.BOLD, "\nDONE\n"))


def clone(repo: str, branch: str = None, cwd: os.PathLike = None):
    if not branch:
        if "@" in repo:
            repo, branch = repo.split("@")
        else:
            branch = "master"

    if which("git") is None:
        raise RuntimeError("Git is not installed.")

    status = call(f"git clone --single-branch --branch {branch} {repo}",
                  shell=True,
                  cwd=cwd)

    if status != 0:
        raise RuntimeError(f"Unable to clone {repo}")


def docker_build(dockerfile: os.PathLike, context: os.PathLike, tag: str,
                 *args):
    print(
        color(bcolors.OKBLUE,
              f"\nBuilding `{color(bcolors.OKGREEN, {tag})}`...\n"))

    call(
        f"docker build -t {tag} -f {dockerfile} {' '.join(args)} .",
        shell=True,
        cwd=context,
    )
