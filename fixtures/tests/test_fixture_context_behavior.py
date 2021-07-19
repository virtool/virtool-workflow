import asyncio

import pytest
from fixtures import fixture_context, get_fixtures, runs_in_new_fixture_context


@pytest.fixture
def fixtures():
    # copy_context=False ensures an empty fixtures dictionary for these tests.
    with fixture_context(copy_context=False):
        yield get_fixtures()


def test_fixture_context_behavior(fixtures):
    fixtures["identity"] = lambda x: x

    with fixture_context() as context_fixtures:
        assert "identity" in context_fixtures

        context_fixtures["foo"] = lambda: "bar"

        assert "foo" in context_fixtures

        # should be working with a copy of the fixture dict
        assert context_fixtures is not fixtures

    assert not "foo" in fixtures

    current_fixtures = get_fixtures()

    # should be back to working with the original dictionary
    assert current_fixtures is fixtures

    def identity(x):
        return x

    with fixture_context(identity):
        context_fixtures = get_fixtures()
        assert "identity" in context_fixtures

        # Make sure "identity" has been overwritten
        assert context_fixtures["identity"] is identity

    # Should still be using the old "identity" fixture here
    assert fixtures["identity"] is not identity


async def test_fixture_context_asyncio_behavior(fixtures):
    fixtures = get_fixtures()

    # Values from the previous test should not be carried forward
    assert "identity" not in fixtures

    fixtures["identity"] = lambda x: x

    async def same_context():
        context_fixtures = get_fixtures()
        assert "identity" in fixtures
        assert context_fixtures is fixtures

        return context_fixtures, fixtures

    context_fixtures, fixtures = await same_context()
    assert context_fixtures is fixtures

    task = asyncio.create_task(same_context())
    context_fixtures, fixtures = await task
    assert context_fixtures is fixtures

    async def different_context():
        with fixture_context():
            context_fixtures = get_fixtures()
            assert "identity" in context_fixtures
            assert context_fixtures is not fixtures

            context_fixtures["foo"] = lambda: "foo"

            assert "foo" in context_fixtures
            assert "foo" not in fixtures

            return context_fixtures

    context_fixtures = await different_context()

    assert "foo" not in fixtures
    assert "foo" in context_fixtures

    task = asyncio.create_task(different_context())
    context_fixtures = await task

    assert "foo" not in fixtures
    assert "foo" in context_fixtures


async def test_fixture_context_no_copy_behavior(fixtures):
    assert len(fixtures) == 0

    fixtures["foo"] = lambda: "foo"

    with fixture_context(lambda: None, copy_context=False) as context_fixtures:
        assert "foo" not in context_fixtures
        assert "<lambda>" in context_fixtures

        context_fixtures["bar"] = lambda: "bar"

    assert "bar" not in fixtures
    assert "<lambda>" not in fixtures


async def test_context_decorator(fixtures):

    def baz():
        return "baz"

    @runs_in_new_fixture_context(baz)
    async def new_context():
        context_fixtures = get_fixtures()
        assert "baz" in context_fixtures
        context_fixtures["foo"] = lambda: "foo"

    await new_context()

    assert "baz" not in fixtures
    assert "foo" not in fixtures

    fixtures["cat"] = lambda: "cat"

    @runs_in_new_fixture_context(baz, copy_context=False)
    async def newer_context():
        context_fixtures = get_fixtures()
        assert "baz" in context_fixtures
        assert "cat" not in context_fixtures

    await newer_context()

    assert "cat" in fixtures
    assert "baz" not in fixtures
