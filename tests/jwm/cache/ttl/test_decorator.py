import collections.abc
import contextlib
import typing
import unittest.mock

import pytest

import jwm._cache.serializers
import jwm._cache.ttl.cache
import jwm._cache.ttl.decorator
import jwm._cache.ttl.local
import jwm._cache.ttl.wrapper

from ..conftest import EMPTY, Empty


def sync_foo(x: int) -> int:
    return x


async def async_foo(x: int) -> int:
    return x


T = typing.TypeVar("T")
P = typing.ParamSpec("P")


@pytest.mark.parametrize(
    "func, return_sync_wrapper",
    (
        (sync_foo, True),
        (async_foo, False),
    ),
)
def test_TTLDecorator(
    func: (
        collections.abc.Callable[P, T]
        | collections.abc.Callable[P, collections.abc.Coroutine[object, object, T]]
    ),
    return_sync_wrapper: bool,
) -> None:
    mock_cache = unittest.mock.Mock()
    mock_serializer = unittest.mock.Mock()
    ttl_decorator = jwm._cache.ttl.decorator.TTLDecorator(
        1, True, b"test_identifier", mock_cache, mock_serializer
    )

    wrapper = ttl_decorator(func)
    if return_sync_wrapper:
        assert isinstance(wrapper, jwm._cache.ttl.wrapper.TTLWrapper)
    else:
        assert isinstance(wrapper, jwm._cache.ttl.wrapper.AsyncTTLWrapper)


@pytest.mark.parametrize(
    "ttl_seconds, typed, identifier, cache, serializer, expected_raises, expected_ttl_seconds, expected_typed, expected_identifier, expected_cache, expected_serializer",
    (
        # ttl_seconds
        (30.0, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, 30.0, EMPTY, EMPTY, EMPTY, EMPTY),
        (0.0, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, 0.0, EMPTY, EMPTY, EMPTY, EMPTY),
        (
            -10.0,
            EMPTY,
            EMPTY,
            EMPTY,
            EMPTY,
            ValueError,
            EMPTY,
            EMPTY,
            EMPTY,
            EMPTY,
            EMPTY,
        ),
        # typed
        (EMPTY, True, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, True, EMPTY, EMPTY, EMPTY),
        (EMPTY, False, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, False, EMPTY, EMPTY, EMPTY),
        # identifier
        (
            EMPTY,
            EMPTY,
            "test-identifier",
            EMPTY,
            EMPTY,
            EMPTY,
            EMPTY,
            EMPTY,
            b"test-identifier",
            EMPTY,
            EMPTY,
        ),
        (EMPTY, EMPTY, "", EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, b"", EMPTY, EMPTY),
        # cache
        (
            EMPTY,
            EMPTY,
            EMPTY,
            jwm._cache.ttl.local.LocalTTLCache(),
            EMPTY,
            EMPTY,
            EMPTY,
            EMPTY,
            EMPTY,
            jwm._cache.ttl.local.LocalTTLCache,
            EMPTY,
        ),
        (
            EMPTY,
            EMPTY,
            EMPTY,
            jwm._cache.ttl.local.AsyncLocalTTLCache(),
            EMPTY,
            EMPTY,
            EMPTY,
            EMPTY,
            EMPTY,
            jwm._cache.ttl.local.AsyncLocalTTLCache,
            EMPTY,
        ),
        (
            EMPTY,
            EMPTY,
            EMPTY,
            "local",
            EMPTY,
            EMPTY,
            EMPTY,
            EMPTY,
            EMPTY,
            jwm._cache.ttl.local.LocalTTLCache,
            EMPTY,
        ),
        (
            EMPTY,
            EMPTY,
            EMPTY,
            "async_local",
            EMPTY,
            EMPTY,
            EMPTY,
            EMPTY,
            EMPTY,
            jwm._cache.ttl.local.AsyncLocalTTLCache,
            EMPTY,
        ),
        # serializer
        (
            EMPTY,
            EMPTY,
            EMPTY,
            EMPTY,
            jwm._cache.serializers.PickleSerializer(),
            EMPTY,
            EMPTY,
            EMPTY,
            EMPTY,
            EMPTY,
            jwm._cache.serializers.PickleSerializer,
        ),
        (
            EMPTY,
            EMPTY,
            EMPTY,
            EMPTY,
            jwm._cache.serializers.JsonSerializer(),
            EMPTY,
            EMPTY,
            EMPTY,
            EMPTY,
            EMPTY,
            jwm._cache.serializers.JsonSerializer,
        ),
        (
            EMPTY,
            EMPTY,
            EMPTY,
            EMPTY,
            "pickle",
            EMPTY,
            EMPTY,
            EMPTY,
            EMPTY,
            EMPTY,
            jwm._cache.serializers.PickleSerializer,
        ),
        (
            EMPTY,
            EMPTY,
            EMPTY,
            EMPTY,
            "json",
            EMPTY,
            EMPTY,
            EMPTY,
            EMPTY,
            EMPTY,
            jwm._cache.serializers.JsonSerializer,
        ),
    ),
)
def test_ttl_cache_decorator_factory(
    ttl_seconds: Empty | float,
    typed: Empty | bool,
    identifier: Empty | bytes,
    cache: (
        Empty | jwm._cache.ttl.cache.TTLCache | jwm._cache.ttl.cache.AsyncTTLCache | str
    ),
    serializer: Empty | jwm._cache.serializers.Serializer | str,
    expected_raises: Empty | Exception | collections.abc.Sequence[Exception],
    expected_ttl_seconds: Empty | float,
    expected_typed: Empty | bool,
    expected_identifier: Empty | bytes,
    expected_cache: (
        Empty
        | typing.Type[
            jwm._cache.ttl.cache.TTLCache | jwm._cache.ttl.cache.AsyncTTLCache
        ]
    ),
    expected_serializer: Empty | typing.Type[jwm._cache.serializers.Serializer],
) -> None:
    with contextlib.ExitStack() as stack:
        if expected_raises is not EMPTY:
            stack.enter_context(pytest.raises(expected_raises))

        kwargs: dict[str, object] = {}
        if ttl_seconds is not EMPTY:
            kwargs["ttl_seconds"] = ttl_seconds
        if typed is not EMPTY:
            kwargs["typed"] = typed
        if identifier is not EMPTY:
            kwargs["identifier"] = identifier
        if cache is not EMPTY:
            kwargs["cache"] = cache
        if serializer is not EMPTY:
            kwargs["serializer"] = serializer

        decorator: jwm._cache.ttl.decorator.TTLDecorator = (
            jwm._cache.ttl.decorator.ttl_cache(**kwargs)
        )

    if expected_raises is not EMPTY:
        return

    if expected_ttl_seconds is not EMPTY:
        assert decorator.ttl_seconds == expected_ttl_seconds
    if expected_typed is not EMPTY:
        assert decorator.typed == expected_typed
    if expected_identifier is not EMPTY:
        assert decorator.identifier == expected_identifier
    if expected_cache is not EMPTY:
        assert isinstance(decorator.cache, expected_cache)
    if expected_serializer is not EMPTY:
        assert isinstance(decorator.serializer, expected_serializer)


def sync_function() -> None:
    return None


async def async_function() -> None:
    return None


P = typing.ParamSpec("P")
T = typing.TypeVar("T")


@pytest.mark.parametrize(
    "function, expected_wrapper",
    (
        (sync_function, jwm._cache.ttl.wrapper.TTLWrapper),
        (async_function, jwm._cache.ttl.wrapper.AsyncTTLWrapper),
    ),
)
def test_ttl_cache_decorator(
    function: collections.abc.Callable[P, T],
    expected_wrapper: typing.Type[
        jwm._cache.ttl.wrapper.TTLWrapper | jwm._cache.ttl.wrapper.AsyncTTLWrapper
    ],
) -> None:
    wrapper = jwm._cache.ttl.decorator.ttl_cache(function)

    assert isinstance(wrapper, expected_wrapper)
