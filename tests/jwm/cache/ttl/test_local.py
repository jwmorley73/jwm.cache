import asyncio
import collections.abc
import time

import pytest

import jwm.cache


@pytest.mark.parametrize(
    "namespace, keys, values",
    (
        (b"test_namespace", (b"a", b"b", b"c"), (b"1", b"2", b"3")),
        (b"test_namespace_2", (b"ca", b"bb", b"ac"), (b"31", b"22", b"13")),
    ),
)
def test_sync_local_single_namespace(
    namespace: bytes,
    keys: collections.abc.Sequence[bytes],
    values: collections.abc.Sequence[bytes],
) -> None:
    local_ = jwm.cache.LocalTTLCache()

    for key, value in zip(keys, values):
        local_.set(namespace, key, value)

    for key, value in zip(keys, values):
        assert local_.get(namespace, key) == value


@pytest.mark.parametrize(
    "namespace, keys, values",
    (
        (b"test_namespace", (b"a", b"b", b"c"), (b"1", b"2", b"3")),
        (b"test_namespace_2", (b"ca", b"bb", b"ac"), (b"31", b"22", b"13")),
    ),
)
async def test_async_local_single_namespace(
    namespace: bytes,
    keys: collections.abc.Sequence[bytes],
    values: collections.abc.Sequence[bytes],
) -> None:
    local_ = jwm.cache.AsyncLocalTTLCache()

    for key, value in zip(keys, values):
        await local_.set(namespace, key, value)

    for key, value in zip(keys, values):
        assert await local_.get(namespace, key) == value


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
def test_sync_local_multiple_namespaces(
    namespaces: collections.abc.Sequence[bytes],
    keyss: collections.abc.Sequence[collections.abc.Sequence[bytes]],
    valuess: collections.abc.Sequence[collections.abc.Sequence[bytes]],
) -> None:
    local_ = jwm.cache.LocalTTLCache()

    for namespace, keys, values in zip(namespaces, keyss, valuess):
        for key, value in zip(keys, values):
            local_.set(namespace, key, value)

    for namespace, keys, values in zip(namespaces, keyss, valuess):
        for key, value in zip(keys, values):
            assert local_.get(namespace, key) == value


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
async def test_async_local_multiple_namespaces(
    namespaces: collections.abc.Sequence[bytes],
    keyss: collections.abc.Sequence[collections.abc.Sequence[bytes]],
    valuess: collections.abc.Sequence[collections.abc.Sequence[bytes]],
) -> None:
    local_ = jwm.cache.AsyncLocalTTLCache()

    for namespace, keys, values in zip(namespaces, keyss, valuess):
        for key, value in zip(keys, values):
            await local_.set(namespace, key, value)

    for namespace, keys, values in zip(namespaces, keyss, valuess):
        for key, value in zip(keys, values):
            assert await local_.get(namespace, key) == value


@pytest.mark.parametrize(
    "namespace, key, value",
    (
        (b"test_namespace", b"a", b"1"),
        (b"test_namespace_2", b"ba", b"21"),
    ),
)
def test_local_clear(namespace: bytes, key: bytes, value: bytes) -> None:
    local_ = jwm.cache.LocalTTLCache()

    local_.set(namespace, key, value)
    assert local_.get(namespace, key) == value
    local_.clear(namespace)
    assert local_.get(namespace, key) is None


@pytest.mark.parametrize(
    "namespace, key, value",
    (
        (b"test_namespace", b"a", b"1"),
        (b"test_namespace_2", b"ba", b"21"),
    ),
)
async def test_async_local_clear(namespace: bytes, key: bytes, value: bytes) -> None:
    local_ = jwm.cache.AsyncLocalTTLCache()

    await local_.set(namespace, key, value)
    assert await local_.get(namespace, key) == value
    await local_.clear(namespace)
    assert await local_.get(namespace, key) is None


@pytest.mark.parametrize(
    "namespace, keys, values",
    (
        (b"test_namespace", (b"a", b"b", b"c"), (b"1", b"2", b"3")),
        (b"test_namespace_2", (b"ca", b"bb", b"ac"), (b"31", b"22", b"13")),
    ),
)
def test_local_size(
    namespace: bytes,
    keys: collections.abc.Sequence[bytes],
    values: collections.abc.Sequence[bytes],
) -> None:
    local_ = jwm.cache.LocalTTLCache()

    for key, value in zip(keys, values):
        local_.set(namespace, key, value)

    assert local_.get_size(namespace) == len(keys)


@pytest.mark.parametrize(
    "namespace, keys, values",
    (
        (b"test_namespace", (b"a", b"b", b"c"), (b"1", b"2", b"3")),
        (b"test_namespace_2", (b"ca", b"bb", b"ac"), (b"31", b"22", b"13")),
    ),
)
async def test_async_local_size(
    namespace: bytes,
    keys: collections.abc.Sequence[bytes],
    values: collections.abc.Sequence[bytes],
) -> None:
    local_ = jwm.cache.AsyncLocalTTLCache()

    for key, value in zip(keys, values):
        await local_.set(namespace, key, value)

    assert await local_.get_size(namespace) == len(keys)


@pytest.mark.parametrize(
    "namespace, key, value, ttl_seconds",
    (
        (b"test_namespace", b"a", b"1", 0.1),
        (b"test_namespace_2", b"ba", b"21", 0),
    ),
)
def test_local_expire(
    namespace: bytes, key: bytes, value: bytes, ttl_seconds: float
) -> None:
    local_ = jwm.cache.LocalTTLCache()

    local_.set(namespace, key, value, ttl_seconds=ttl_seconds)

    time.sleep(ttl_seconds + 0.1)
    assert local_.get(namespace, key) == None


@pytest.mark.parametrize(
    "namespace, key, value, ttl_seconds",
    (
        (b"test_namespace", b"a", b"1", 0.1),
        (b"test_namespace_2", b"ba", b"21", 0),
    ),
)
async def test_async_local_expire(
    namespace: bytes, key: bytes, value: bytes, ttl_seconds: float
) -> None:
    local_ = jwm.cache.AsyncLocalTTLCache()

    await local_.set(namespace, key, value, ttl_seconds=ttl_seconds)

    await asyncio.sleep(ttl_seconds + 0.1)
    assert await local_.get(namespace, key) == None
