from fixtures import fixture
from virtool_workflow import Workflow


@fixture
def fixture_a() -> str:
    return "a"


@fixture
def fixture_b(fixture_a: str) -> str:
    return f"{fixture_a}b"


@fixture
async def fixture_c() -> str:
    return "c"


wf = Workflow()


@wf.step
def start(fixture_a, fixture_b, fixture_c, results):
    results["fixture_a"] = fixture_a
    results["fixture_b"] = fixture_b
    results["fixture_c"] = fixture_c

    return "In file fixtures are correctly loaded"
