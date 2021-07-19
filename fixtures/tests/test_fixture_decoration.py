from fixtures import (Fixture, fixture, fixture_context, get_fixtures,
                      runs_in_new_fixture_context)


@fixture
def module_level_fixture():
    ...


@runs_in_new_fixture_context()
async def test_fixture_definition_semantics():
    @fixture
    def a():
        ...

    fixtures = get_fixtures()

    # Fixtures defined at module level should always be available.
    assert module_level_fixture.__name__ in fixtures

    assert "a" in fixtures
    assert fixtures["a"] is a

    with fixture_context() as context_fixtures:
        assert module_level_fixture.__name__ in fixtures

        @fixture
        def b():
            ...

        # The 'b' fixture was created in this context, so it should be seen here.
        assert "b" in context_fixtures
        assert context_fixtures["b"] is b

    # 'b' fixture was created in a sub-context, so shouldn't be seen here.
    assert "b" not in fixtures

    with fixture_context(copy_context=False) as context_fixtures:
        # Should have an empty context here, even though there are module level fixtures.
        assert len(context_fixtures) == 0


@runs_in_new_fixture_context(copy_context=False)
async def test_fixture_isinstance_check():

    @fixture
    def c():
        ...

    def d():
        ...

    assert isinstance(c, Fixture)
    assert not isinstance(d, Fixture)
