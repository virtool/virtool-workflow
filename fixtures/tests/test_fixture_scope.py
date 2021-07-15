import asyncio
import pytest
from fixtures import FixtureScope, fixture

async def test_instantiation_of_fixture_types():
    # Create futures to check which functions have been called.
    sync_called = asyncio.Future()
    async_called = asyncio.Future()
    gen_called = asyncio.Future()
    gen_finished = asyncio.Future()
    async_gen_called = asyncio.Future()
    async_gen_finished = asyncio.Future()

    @fixture
    def sync_fixture():
        sync_called.set_result(True)

    @fixture
    async def async_fixture():
        async_called.set_result(True)

    @fixture
    def generator_fixture():
        gen_called.set_result(True)
        try:
            yield
        finally:
            gen_finished.set_result(True)


    @fixture
    async def async_gen_fixture():
        async_gen_called.set_result(True)
        try:
            yield
        finally:
            async_gen_finished.set_result(True)

    # Instantiate each fixture type and assert they have been called.
    async with FixtureScope() as scope:
        await scope._instantiate(sync_fixture)
        assert sync_called.result() is True

        await scope._instantiate(async_fixture)
        assert async_called.result() is True

        await scope._instantiate(generator_fixture)
        assert gen_called.result() is True

        await scope._instantiate(async_gen_fixture)
        assert async_gen_called.result() is True

    # Generator fixtures should have been finished out on `__aexit__`
    assert gen_finished.result() is True
    assert async_gen_finished.result() is True

    # Reset futures for failure case
    gen_called = asyncio.Future()
    gen_finished = asyncio.Future()
    async_gen_called = asyncio.Future()
    async_gen_finished = asyncio.Future()

    with pytest.raises(RuntimeError):
        async with FixtureScope() as scope:
            await scope._instantiate(generator_fixture)
            assert gen_called.result() is True

            await scope._instantiate(async_gen_fixture)
            assert async_gen_called.result() is True

            raise RuntimeError()

    # Generator fixtures should still get closed out when there is a failure.

    assert gen_finished.result() is True
    assert async_gen_finished.result() is True