import asyncio

import pytest
from fixtures import FixtureScope, fixture, runs_in_new_fixture_context
from virtool_workflow import Workflow


@runs_in_new_fixture_context(copy_context=False)
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


@runs_in_new_fixture_context(copy_context=False)
async def test_does_not_wrap_noarg_function():
    no_args_called = asyncio.Future()

    async def no_args():
        no_args_called.set_result(True)

    async with FixtureScope() as scope:
        bound = await scope.bind(no_args)
        await bound()

        # A function with no arguments should not be wrapped.
        assert bound is no_args


@runs_in_new_fixture_context(copy_context=False)
async def test_non_recursive_bind_posargs():

    @fixture
    def a():
        return "a"

    @fixture
    def b():
        return "b"

    @fixture
    def c():
        return "c"

    def with_args(a, b, c, d="d"):
        return a + b + c + d

    async with FixtureScope() as scope:
        bound = await scope.bind(with_args)

        # Function should have been wrapped.
        assert bound is not with_args
        assert bound() == "abcd"
        assert bound(c="C") == "abCd"
        assert bound("A", "B") == "ABcd"

        @fixture
        def d():
            return "dd"

        # `d` fixture should not be used, since it wasn't available when `bind` was called.
        assert bound() == "abcd"

        bound = await scope.bind(with_args)

        # Now  `d` fixture should be used after re-binding.
        assert bound("A", "B", c="C") == "ABCdd"


@runs_in_new_fixture_context(copy_context=False)
async def test_recursive_bind_posargs():
    @fixture
    def a():
        return "a"

    @fixture
    def ab(a):
        return a + "b"

    @fixture
    def c():
        return "c"

    @fixture
    def abc(ab, c):
        return ab + c

    @fixture
    def letters(abc, a, ab, c):
        return abc + a + ab + c

    def check_letters(letters, ab, a, c, b):
        return letters == ab + c + a + a + b + c

    async with FixtureScope() as scope:
        bound = await scope.bind(check_letters, b="b")

        assert bound() is True


@runs_in_new_fixture_context(copy_context=False)
async def test_mutable_fixture_semantics():
    @fixture
    def dictionary():
        return {}

    workflow = Workflow()

    @workflow.step
    async def step1(dictionary):
        return dictionary

    @workflow.step
    async def step2(dictionary):
        return dictionary

    async with FixtureScope() as scope:
        await workflow.bind_to_fixtures(scope)

        d3 = await workflow.steps[0]()
        d4 = await workflow.steps[1]()

        assert d3 is d4 is scope["dictionary"] is not None
