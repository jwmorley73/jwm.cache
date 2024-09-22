import pytest

import jwm.cache


class TestCache():
    def foo(self, bar: str) -> str:
        return bar

def test_initial_cache() -> None:
    test_cache = TestCache()

    forward_cache = jwm.cache.ForwardDeclared(initial_object=test_cache)

    assert forward_cache.object == test_cache

def test_set_cache() -> None:
    test_cache = TestCache()

    forward_cache = jwm.cache.ForwardDeclared()
    forward_cache.set_object(test_cache)

    assert forward_cache.object == test_cache

def test_get_cache_attribute() -> None:
    test_cache = TestCache()

    forward_cache = jwm.cache.ForwardDeclared()
    forward_cache.set_object(test_cache)

    assert forward_cache.foo("test") == "test"

def test_unset_cache() -> None:
    forward_cache = jwm.cache.ForwardDeclared()
    
    with pytest.raises(NotImplementedError):
        forward_cache.foo
