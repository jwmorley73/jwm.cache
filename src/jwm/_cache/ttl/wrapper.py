from __future__ import annotations

import asyncio
import collections.abc
import functools
import inspect
import sys
import typing

import jwm._cache.hash_
import jwm._cache.serializers
import jwm._cache.sync
import jwm._cache.ttl.cache


class TTLInfo(typing.NamedTuple):
    "Statistics about Time To Live (TTL) wrapper performance"
    hits: int
    misses: int
    current_size: int


class TTLParameters(typing.NamedTuple):
    "Parameters about how a Time To Live (TTL) wrapper was constructed"
    ttl_seconds: float
    typed: bool
    identifier: bytes
    cache: jwm._cache.ttl.cache.TTLCache | jwm._cache.ttl.cache.AsyncTTLCache
    serializer: jwm._cache.serializers.Serializer


P0 = typing.ParamSpec("P0")
T0 = typing.TypeVar("T0")


class TTLWrapper(typing.Generic[P0, T0]):
    "Time To Live (TTL) wrapper returned by ttl_cache or TTLDecorator"

    def __init__(
        self,
        func: collections.abc.Callable[P0, T0],
        ttl_seconds: float,
        typed: bool,
        identifier: bytes,
        cache: jwm._cache.ttl.cache.TTLCache | jwm._cache.ttl.cache.AsyncTTLCache,
        serializer: jwm._cache.serializers.Serializer,
    ) -> None:
        self: TTLWrapper[P0, T0] = functools.update_wrapper(self, func)

        self.__wrapped__: collections.abc.Callable[P0, T0] = func
        self._ttl_seconds = ttl_seconds
        self._typed = typed
        self._identifier = identifier
        self._cache = cache
        self._serializer = serializer

        self._signature = inspect.signature(self.__wrapped__)
        self._hits = 0
        self._misses = 0
        self._wrapped_self: typing.Any | None = None

    def __get__(self, obj: typing.Any, _: typing.Type | None) -> TTLWrapper[P0, T0]:
        self._wrapped_self = obj
        return self

    def __call__(self, *args: P0.args, **kwargs: P0.kwargs) -> T0:
        # Bind arguments with defaults
        if self._wrapped_self is not None:
            bound = self._signature.bind(self._wrapped_self, *args, **kwargs)
        else:
            bound = self._signature.bind(*args, **kwargs)
        bound.apply_defaults()

        # Get hash of bound arguments
        hash_ = jwm._cache.hash_.hash_bound(
            bound,
            typed=self._typed,
        ).to_bytes(sys.hash_info.width, "little")

        # Check for Cache hit
        value = self._cache.get(self._identifier, hash_)
        if asyncio.iscoroutine(value):
            try:
                value = jwm._cache.sync.run_coroutine_in_thread(value)
            except RuntimeError as error:
                raise RuntimeError(
                    "Cannot use AsyncTTLCache outside a running event loop."
                ) from error
        if value is not None:
            self._hits += 1
            return self._serializer.deserialize(value)
        self._misses += 1

        # Run original function and store result in cache
        value = self.__wrapped__(*bound.args, **bound.kwargs)
        set_ = self._cache.set(
            self._identifier,
            hash_,
            self._serializer.serialize(value),
            self._ttl_seconds,
        )
        if asyncio.iscoroutine(set_):
            try:
                jwm._cache.sync.run_coroutine_in_thread(set_)
            except RuntimeError as error:
                raise RuntimeError(
                    "Cannot use AsyncTTLCache outside a running event loop."
                ) from error

        return value

    def cache_info(self) -> TTLInfo:
        """Report cache statistics"""
        size = self._cache.get_size(self._identifier)
        if asyncio.iscoroutine(size):
            try:
                size = jwm._cache.sync.run_coroutine_in_thread(size)
            except RuntimeError as error:
                raise RuntimeError(
                    "Cannot use AsyncTTLCache outside a running event loop."
                ) from error

        return TTLInfo(
            self._hits,
            self._misses,
            size,
        )

    def cache_clear(self) -> None:
        """Clear the cache and cache statistics"""
        self._hits = 0
        self._misses = 0
        clear = self._cache.clear(self._identifier)
        if asyncio.iscoroutine(clear):
            try:
                jwm._cache.sync.run_coroutine_in_thread(clear)
            except RuntimeError as error:
                raise RuntimeError(
                    "Cannot use AsyncTTLCache outside a running event loop."
                ) from error

    def cache_parameters(self) -> TTLParameters:
        """Report cache configuration"""
        return TTLParameters(
            self._ttl_seconds,
            self._typed,
            self._identifier,
            self._cache,
            self._serializer,
        )


P1 = typing.ParamSpec("P1")
T1 = typing.TypeVar("T1")


class AsyncTTLWrapper(typing.Generic[P1, T1]):
    "Async Time To Live (TTL) wrapper returned by ttl_cache or TTLDecorator"

    def __init__(
        self,
        func: collections.abc.Callable[
            P1, collections.abc.Coroutine[typing.Any, typing.Any, T1]
        ],
        ttl_seconds: float,
        typed: bool,
        identifier: bytes,
        cache: jwm._cache.ttl.cache.AsyncTTLCache | jwm._cache.ttl.cache.TTLCache,
        serializer: jwm._cache.serializers.Serializer,
    ) -> None:
        self: AsyncTTLWrapper[P1, T1] = functools.update_wrapper(self, func)

        self.__wrapped__: collections.abc.Callable[
            P1, collections.abc.Coroutine[typing.Any, typing.Any, T1]
        ] = func
        self._ttl_seconds = ttl_seconds
        self._typed = typed
        self._identifier = identifier
        self._cache = cache
        self._serializer = serializer

        self._signature = inspect.signature(self.__wrapped__)
        self._hits = 0
        self._misses = 0
        self._wrapped_self: typing.Any | None = None

    def __get__(
        self, obj: typing.Any, _: typing.Type | None
    ) -> AsyncTTLWrapper[P1, T1]:
        self._wrapped_self = obj
        return self

    async def __call__(self, *args: P1.args, **kwargs: P1.kwargs) -> T1:
        # Bind arguments with defaults
        if self._wrapped_self is not None:
            bound = self._signature.bind(self._wrapped_self, *args, **kwargs)
        else:
            bound = self._signature.bind(*args, **kwargs)

        # Get hash of bound arguments
        hash_ = jwm._cache.hash_.hash_bound(
            bound,
            typed=self._typed,
        ).to_bytes(sys.hash_info.width, "little")

        # Check for Cache hit
        value = self._cache.get(self._identifier, hash_)
        if asyncio.iscoroutine(value):
            value = await value
        if value is not None:
            self._hits += 1
            return self._serializer.deserialize(value)
        self._misses += 1

        # Run original function and store result in cache
        value = await self.__wrapped__(*bound.args, **bound.kwargs)
        set_ = self._cache.set(
            self._identifier,
            hash_,
            self._serializer.serialize(value),
            self._ttl_seconds,
        )
        if asyncio.iscoroutine(set_):
            await set_

        return value

    async def cache_info(self) -> TTLInfo:
        """Report cache statistics"""
        size = self._cache.get_size(self._identifier)
        if asyncio.iscoroutine(size):
            size = await size

        return TTLInfo(
            self._hits,
            self._misses,
            size,
        )

    async def cache_clear(self) -> None:
        """Clear the cache and cache statistics"""
        self._hits = 0
        self._misses = 0
        clear = self._cache.clear(self._identifier)
        if asyncio.iscoroutine(clear):
            await clear

    def cache_parameters(self) -> TTLParameters:
        """Report cache configuration"""
        return TTLParameters(
            self._ttl_seconds,
            self._typed,
            self._identifier,
            self._cache,
            self._serializer,
        )
