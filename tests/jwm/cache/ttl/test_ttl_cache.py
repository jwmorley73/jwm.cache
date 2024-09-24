import jwm.cache


@jwm.cache.ttl_cache
def simple_decorator(x: str) -> str:
    return x

def test_simple() -> None:
    a1 = simple_decorator("a")
    a2 = simple_decorator("a")
    info = simple_decorator.cache_info()

    assert a1 == a2
    assert info.hits == 1
    assert info.misses == 1
    assert info.current_size == 1

@jwm.cache.ttl_cache()
def simple_decorator_factory(x: str) -> str:
    return x

def test_simple_decorator_factory() -> None:
    a1 = simple_decorator_factory("a")
    a2 = simple_decorator_factory("a")
    info = simple_decorator_factory.cache_info()

    assert a1 == a2
    assert info.hits == 1
    assert info.misses == 1
    assert info.current_size == 1

@jwm.cache.ttl_cache()
def empty_decorator() -> str:
    return "test"

def test_empty_decorator() -> None:
    a1 = empty_decorator()
    a2 = empty_decorator()
    info = simple_decorator_factory.cache_info()

    assert a1 == a2
    assert info.hits == 1
    assert info.misses == 1
    assert info.current_size == 1

