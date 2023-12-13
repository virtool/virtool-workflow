import logging

from virtool_workflow.api.utils import retry


async def test_retry(caplog):
    """
    Test that the retry utility retries failing HTTP requests and logs the attempts.
    """
    caplog.set_level(logging.INFO)

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

    for record in caplog.records:
        assert record.levelno == logging.INFO
        assert (
            record.msg == "Encountered ConnectionRefusedError. Retrying in 5 seconds."
        )
