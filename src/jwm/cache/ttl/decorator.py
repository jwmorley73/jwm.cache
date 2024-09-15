from __future__ import annotations

import asyncio
import collections.abc
import typing
import uuid

import jwm.cache.forward
import jwm.cache.serializers
import jwm.cache.ttl.cache
import jwm.cache.ttl.default
import jwm.cache.ttl.local
import jwm.cache.ttl.wrapper

P0 = typing.ParamSpec("P0")
T0 = typing.TypeVar("T0")


class TTLDecorator:
    "Time To Live (TTL) decorator returned by ttl_cache"

    def __init__(
        self,
        ttl_seconds: float,
        typed: bool,
        identifier: bytes,
        cache: jwm.cache.ttl.cache.TTLCache | jwm.cache.ttl.cache.AsyncTTLCache,
        serializer: jwm.cache.serializers.Serializer,
    ) -> None:
        self._ttl_seconds = ttl_seconds
        self._typed = typed
        self._identifier = identifier
        self._cache = cache
        self._serializer = serializer

    @typing.overload
    def __call__(
        self,
        func: collections.abc.Callable[
            P0, collections.abc.Coroutine[typing.Any, typing.Any, T0]
        ],
    ) -> jwm.cache.ttl.wrapper.AsyncTTLWrapper[P0, T0]: ...

    @typing.overload
    def __call__(
        self, func: collections.abc.Callable[P0, T0]
    ) -> jwm.cache.ttl.wrapper.TTLWrapper[P0, T0]: ...

    def __call__(
        self,
        func: (
            collections.abc.Callable[P0, T0]
            | collections.abc.Callable[
                P0, collections.abc.Coroutine[typing.Any, typing.Any, T0]
            ]
        ),
    ) -> (
        jwm.cache.ttl.wrapper.TTLWrapper[P0, T0]
        | jwm.cache.ttl.wrapper.AsyncTTLWrapper[P0, T0]
    ):
        if asyncio.iscoroutinefunction(func):
            return jwm.cache.ttl.wrapper.AsyncTTLWrapper[P0, T0](
                func,
                self._ttl_seconds,
                self._typed,
                self._identifier,
                self._cache,
                self._serializer,
            )
        else:
            return jwm.cache.ttl.wrapper.TTLWrapper[P0, T0](
                func,
                self._ttl_seconds,
                self._typed,
                self._identifier,
                self._cache,
                self._serializer,
            )


P1 = typing.ParamSpec("P1")
T1 = typing.TypeVar("T1")


@typing.overload
def ttl_cache(
    ttl_seconds: float = 60,
    typed: bool = False,
    *,
    identifier: str | None = None,
    cache: (
        jwm.cache.ttl.cache.TTLCache
        | jwm.cache.ttl.cache.AsyncTTLCache
        | typing.Literal["local", "async_local"]
    ) = "local",
    serializer: (
        jwm.cache.serializers.Serializer | typing.Literal["pickle", "json"]
    ) = "pickle",
) -> TTLDecorator: ...


@typing.overload
def ttl_cache(
    func: collections.abc.Callable[
        P1, collections.abc.Coroutine[typing.Any, typing.Any, T1]
    ]
) -> jwm.cache.ttl.wrapper.AsyncTTLWrapper[P1, T1]: ...


@typing.overload
def ttl_cache(
    func: collections.abc.Callable[P1, T1]
) -> jwm.cache.ttl.wrapper.TTLWrapper[P1, T1]: ...


def ttl_cache(
    ttl_seconds: (
        float
        | collections.abc.Callable[P1, T1]
        | collections.abc.Callable[
            P1, collections.abc.Coroutine[typing.Any, typing.Any, T1]
        ]
    ) = 60,
    typed: bool = False,
    *,
    identifier: str | None = None,
    cache: (
        jwm.cache.ttl.cache.TTLCache
        | jwm.cache.ttl.cache.AsyncTTLCache
        | typing.Literal["local", "async_local", "default"]
    ) = "default",
    serializer: (
        jwm.cache.serializers.Serializer | typing.Literal["pickle", "json"]
    ) = "pickle",
) -> (
    TTLDecorator
    | jwm.cache.ttl.wrapper.TTLWrapper[P1, T1]
    | jwm.cache.ttl.wrapper.AsyncTTLWrapper[P1, T1]
):
    """Function caching decorator with entries having a constrained Time To
    Live (TTL).

    Heavily inspired by the standard libraries `functools.lru_cache` and
    provides a similar API. This includes `cache_info`, `cache_clear` and
    `cache_properties` methods on the wrapper. Optional type consideration
    is also supported.

    There are a number of extra features `ttl_cache` offers compared to
    `functools.lru_cache` (usually at the cost of speed):
     - Supports async functions
     - Supports default arguments being considered as part of the cache key
     - Allows custom cache to be used as a backend
       - Supports mix and match async and sync functions with async and sync
         caches
     - Optional identifier so multiple functions may share a cache
       - If no identifier is provided, functions that share a cache are split
         into separate namespaces
     - Allows custom serializers
     - Wrappers are class instances rather than functions (avoids typing
         hinting gymnastics)
     - Uses a persistent hash function for creating cache keys (pythons default
         `hash` function as used by `functools.lru_cache` returns different
         hashes for different runs for security reasons).
       - You can implement the `__persistent_hash__` method to control how your
         object is hashed.

    Args:
        ttl_seconds (float | Callable[P1, T1] | Callable[P1, Coroutine[Any, Any, T1]], optional):
            Time to live for the entries if used as a decorator factory,
            function to be wrapped if not. Defaults to 60.
        typed (bool, optional): Whether to consider types when creating the
            cache key. Defaults to False.
        identifier (str | None, optional): Used to allow multiple functions to
            share a cache. Defaults to a random string which isolates the
            functions.
        cache (TTLCache | AsyncTTLCache | Literal["local", "async_local", "default"], optional):
            Cache where the values will be stored. Defaults to "default" (which
            will use the global default).
        serializer (Serializer  |  Literal["pickle", "json"], optional):
            Serializer to use when creating keys and storing values in the
            cache. Defaults to "pickle".

    Returns:
        TTLDecorator | TTLWrapper[P1, T1] | AsyncTTLWrapper[P1, T1]: A
            decorator is returned if using this function as a decorator
            factory, else the appropriate wrapper is returned depending on
            whether the supplied function is async or not.
    """
    if callable(ttl_seconds):
        return ttl_cache()(ttl_seconds)

    if ttl_seconds < 0:
        raise ValueError("ttl_seconds must be greater than or equal to zero.")

    if identifier is None:
        _identifier = uuid.uuid4().bytes
    else:
        _identifier = identifier.encode("utf-8")

    match cache:
        case "local":
            cache = jwm.cache.ttl.local.LocalTTLCache()
        case "async_local":
            cache = jwm.cache.ttl.local.AsyncLocalTTLCache()
        case "default":
            cache = jwm.cache.ttl.default.DEFAULT_CACHE
        case _:
            pass

    match serializer:
        case "pickle":
            serializer = jwm.cache.serializers.PickleSerializer()
        case "json":
            serializer = jwm.cache.serializers.JsonSerializer()
        case _:
            pass

    return TTLDecorator(ttl_seconds, typed, _identifier, cache, serializer)
