from pathlib import Path
from virtool_workflow.storage.paths import context_directory


def test_context_directory():
    with context_directory("foobar") as foobar:
        with (foobar/"cat").open("w") as cat:
            cat.write("cat")

        assert foobar.exists()
        assert (foobar/"cat").exists()

    assert not Path("foobar").exists()
    assert not Path("foobar/cat").exists()

