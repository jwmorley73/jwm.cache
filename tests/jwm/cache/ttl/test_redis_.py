import asyncio
import collections.abc
import time

import fakeredis
import pytest

import jwm.cache


@pytest.fixture
def sync_redis_client() -> fakeredis.FakeRedis:
    return fakeredis.FakeRedis()


@pytest.fixture
def async_redis_client() -> fakeredis.FakeAsyncRedis:
    return fakeredis.FakeAsyncRedis()


@pytest.fixture
def sync_redis_ttl_cache(sync_redis_client) -> jwm.cache.RedisTTLCache:
    return jwm.cache.RedisTTLCache(sync_redis_client)


@pytest.fixture
def async_redis_ttl_cache(async_redis_client) -> jwm.cache.AsyncRedisTTLCache:
    return jwm.cache.AsyncRedisTTLCache(async_redis_client)


@pytest.mark.parametrize(
    "namespace, keys, values",
    (
        (b"test_namespace", (b"a", b"b", b"c"), (b"1", b"2", b"3")),
        (b"test_namespace_2", (b"ca", b"bb", b"ac"), (b"31", b"22", b"13")),
    ),
)
def test_sync_redis_single_namespace(
    namespace: bytes,
    keys: collections.abc.Sequence[bytes],
    values: collections.abc.Sequence[bytes],
    sync_redis_ttl_cache: jwm.cache.RedisTTLCache,
) -> None:
    for key, value in zip(keys, values):
        sync_redis_ttl_cache.set(namespace, key, value)

    for key, value in zip(keys, values):
        assert sync_redis_ttl_cache.get(namespace, key) == value


@pytest.mark.parametrize(
    "namespace, keys, values",
    (
        (b"test_namespace", (b"a", b"b", b"c"), (b"1", b"2", b"3")),
        (b"test_namespace_2", (b"ca", b"bb", b"ac"), (b"31", b"22", b"13")),
    ),
)
async def test_async_redis_single_namespace(
    namespace: bytes,
    keys: collections.abc.Sequence[bytes],
    values: collections.abc.Sequence[bytes],
    async_redis_ttl_cache: jwm.cache.AsyncRedisTTLCache,
) -> None:
    for key, value in zip(keys, values):
        await async_redis_ttl_cache.set(namespace, key, value)

    for key, value in zip(keys, values):
        assert await async_redis_ttl_cache.get(namespace, key) == value


@pytest.mark.parametrize(
    "namespaces, keyss, valuess",
    (
        (
            (b"test_namespace_a", b"test_namespace_b"),
            ((b"a", b"b", b"c"), (b"d", b"e", b"f")),
            ((b"1", b"2", b"3"), (b"4", b"5", b"6")),
        ),
        (
            (b"test_namespace_2", b"test_namespace_1"),
            ((b"fa", b"eb", b"dc"), (b"cd", b"be", b"af")),
            ((b"61", b"52", b"43"), (b"34", b"25", b"16")),
        ),
    ),
)
def test_sync_redis_multiple_namespaces(
    namespaces: collections.abc.Sequence[bytes],
    keyss: collections.abc.Sequence[collections.abc.Sequence[bytes]],
    valuess: collections.abc.Sequence[collections.abc.Sequence[bytes]],
    sync_redis_ttl_cache: jwm.cache.RedisTTLCache,
) -> None:
    for namespace, keys, values in zip(namespaces, keyss, valuess):
        for key, value in zip(keys, values):
            sync_redis_ttl_cache.set(namespace, key, value)

    for namespace, keys, values in zip(namespaces, keyss, valuess):
        for key, value in zip(keys, values):
            assert sync_redis_ttl_cache.get(namespace, key) == value


@pytest.mark.parametrize(
    "namespaces, keyss, valuess",
    (
        (
            (b"test_namespace_a", b"test_namespace_b"),
            ((b"a", b"b", b"c"), (b"d", b"e", b"f")),
            ((b"1", b"2", b"3"), (b"4", b"5", b"6")),
        ),
        (
            (b"test_namespace_2", b"test_namespace_1"),
            ((b"fa", b"eb", b"dc"), (b"cd", b"be", b"af")),
            ((b"61", b"52", b"43"), (b"34", b"25", b"16")),
        ),
    ),
)
async def test_async_redis_multiple_namespaces(
    namespaces: collections.abc.Sequence[bytes],
    keyss: collections.abc.Sequence[collections.abc.Sequence[bytes]],
    valuess: collections.abc.Sequence[collections.abc.Sequence[bytes]],
    async_redis_ttl_cache: jwm.cache.AsyncRedisTTLCache,
) -> None:
    for namespace, keys, values in zip(namespaces, keyss, valuess):
        for key, value in zip(keys, values):
            await async_redis_ttl_cache.set(namespace, key, value)

    for namespace, keys, values in zip(namespaces, keyss, valuess):
        for key, value in zip(keys, values):
            assert await async_redis_ttl_cache.get(namespace, key) == value


@pytest.mark.parametrize(
    "namespace, key, value",
    (
        (b"test_namespace", b"a", b"1"),
        (b"test_namespace_2", b"ba", b"21"),
    ),
)
def test_redis_clear(
    namespace: bytes,
    key: bytes,
    value: bytes,
    sync_redis_ttl_cache: jwm.cache.RedisTTLCache,
) -> None:
    sync_redis_ttl_cache.set(namespace, key, value)
    assert sync_redis_ttl_cache.get(namespace, key) == value
    sync_redis_ttl_cache.clear(namespace)
    assert sync_redis_ttl_cache.get(namespace, key) is None


@pytest.mark.parametrize(
    "namespace, key, value",
    (
        (b"test_namespace", b"a", b"1"),
        (b"test_namespace_2", b"ba", b"21"),
    ),
)
async def test_async_redis_clear(
    namespace: bytes,
    key: bytes,
    value: bytes,
    async_redis_ttl_cache: jwm.cache.AsyncRedisTTLCache,
) -> None:
    await async_redis_ttl_cache.set(namespace, key, value)
    assert await async_redis_ttl_cache.get(namespace, key) == value
    await async_redis_ttl_cache.clear(namespace)
    assert await async_redis_ttl_cache.get(namespace, key) is None


@pytest.mark.parametrize(
    "namespace, keys, values",
    (
        (b"test_namespace", (b"a", b"b", b"c"), (b"1", b"2", b"3")),
        (b"test_namespace_2", (b"ca", b"bb", b"ac"), (b"31", b"22", b"13")),
    ),
)
def test_redis_size(
    namespace: bytes,
    keys: collections.abc.Sequence[bytes],
    values: collections.abc.Sequence[bytes],
    sync_redis_ttl_cache: jwm.cache.RedisTTLCache,
) -> None:
    for key, value in zip(keys, values):
        sync_redis_ttl_cache.set(namespace, key, value)
    assert sync_redis_ttl_cache.get_size(namespace) == len(keys)


@pytest.mark.parametrize(
    "namespace, keys, values",
    (
        (b"test_namespace", (b"a", b"b", b"c"), (b"1", b"2", b"3")),
        (b"test_namespace_2", (b"ca", b"bb", b"ac"), (b"31", b"22", b"13")),
    ),
)
async def test_async_redis_size(
    namespace: bytes,
    keys: collections.abc.Sequence[bytes],
    values: collections.abc.Sequence[bytes],
    async_redis_ttl_cache: jwm.cache.AsyncRedisTTLCache,
) -> None:
    for key, value in zip(keys, values):
        await async_redis_ttl_cache.set(namespace, key, value)
    assert await async_redis_ttl_cache.get_size(namespace) == len(keys)


@pytest.mark.parametrize(
    "namespace, key, value, ttl_seconds",
    (
        (b"test_namespace", b"a", b"1", 0.1),
        (b"test_namespace_2", b"ba", b"21", 0),
    ),
)
def test_redis_expire(
    namespace: bytes,
    key: bytes,
    value: bytes,
    ttl_seconds: float,
    sync_redis_ttl_cache: jwm.cache.RedisTTLCache,
) -> None:
    sync_redis_ttl_cache.set(namespace, key, value, ttl_seconds=ttl_seconds)
    time.sleep(ttl_seconds + 0.1)
    assert sync_redis_ttl_cache.get(namespace, key) == None


@pytest.mark.parametrize(
    "namespace, key, value, ttl_seconds",
    (
        (b"test_namespace", b"a", b"1", 0.1),
        (b"test_namespace_2", b"ba", b"21", 0),
    ),
)
async def test_async_redis_expire(
    namespace: bytes,
    key: bytes,
    value: bytes,
    ttl_seconds: float,
    async_redis_ttl_cache: jwm.cache.AsyncRedisTTLCache,
) -> None:
    await async_redis_ttl_cache.set(namespace, key, value, ttl_seconds=ttl_seconds)
    await asyncio.sleep(ttl_seconds + 0.1)
    assert await async_redis_ttl_cache.get(namespace, key) == None
