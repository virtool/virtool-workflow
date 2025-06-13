from pytest_structlog import StructuredLogCapture

from virtool_workflow.api.utils import retry


async def test_retry(log: StructuredLogCapture):
    """Test that the retry utility retries failing HTTP requests and logs the attempts."""

    class Retry:
        def __init__(self):
            self.attempt = 0
            self.args = []
            self.kwargs = {}

        @retry
        async def do_something(self, *args, **kwargs):
            self.attempt += 1

            if self.attempt == 1:
                raise ConnectionRefusedError

            self.args = args
            self.kwargs = kwargs

    obj = Retry()

    await obj.do_something("hello", this_is_a_test=True)

    assert obj.attempt == 2
    assert obj.args == ("hello",)
    assert obj.kwargs == {"this_is_a_test": True}
    assert log.has("Encountered ConnectionRefusedError. Retrying in 5 seconds.")
