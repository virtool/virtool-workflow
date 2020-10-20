from virtool_workflow import fixture


@fixture
def fixture_a() -> str:
    return "a"


@fixture
def fixture_b(a: str) -> str:
    return f"{a}b"


@fixture
async def fixture_c() -> str:
    return "c"
