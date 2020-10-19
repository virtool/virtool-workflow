from virtool_workflow import fixture


@fixture
def number_of_processes() -> int:
    # TODO: load virtool config
    return 3