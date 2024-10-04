
import jwm.cache


@jwm.cache.ttl_cache
def sync_decorator(x: str, y: int) -> tuple[str, int]:
    return (x, y)


def test_sync_decorator() -> None:
    a1 = sync_decorator("a", 1)
    a2 = sync_decorator("a", 1)
    info = sync_decorator.cache_info()

    assert a1 == a2
    assert info.hits == 1
    assert info.misses == 1
    assert info.current_size == 1


@jwm.cache.ttl_cache
async def async_decorator(x: str, y: int) -> tuple[str, int]:
    return (x, y)


async def test_async_decorator() -> None:
    a1 = await async_decorator("a", 1)
    a2 = await async_decorator("a", 1)
    info = await async_decorator.cache_info()

    assert a1 == a2
    assert info.hits == 1
    assert info.misses == 1
    assert info.current_size == 1


@jwm.cache.ttl_cache()
def sync_decorator_factory(x: str, y: int) -> tuple[str, int]:
    return (x, y)

t = jwm.cache.ttl_cache()

def test_sync_decorator_factory() -> None:
    a1 = sync_decorator_factory("a", 1)
    a2 = sync_decorator_factory("a", 1)
    info = sync_decorator_factory.cache_info()

    assert a1 == a2
    assert info.hits == 1
    assert info.misses == 1
    assert info.current_size == 1


@jwm.cache.ttl_cache()
async def async_decorator_factory(x: str, y: int) -> tuple[str, int]:
    return (x, y)


async def test_async_decorator_factory() -> None:
    a1 = await async_decorator_factory("a", 1)
    a2 = await async_decorator_factory("a", 1)
    info = await async_decorator_factory.cache_info()

    assert a1 == a2
    assert info.hits == 1
    assert info.misses == 1
    assert info.current_size == 1
