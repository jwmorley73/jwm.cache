import asyncio
import threading

import jwm._cache.ttl.cache


class LocalTTLCache(jwm._cache.ttl.cache.TTLCache):
    def __init__(self) -> None:
        self._cache: dict[bytes, dict[bytes, bytes]] = {}
        self._ttl_timers: dict[bytes, dict[bytes, threading.Timer]] = {}
        self._lock = threading.Lock()

    def get(self, namespace: bytes, key: bytes) -> bytes:
        return self._cache.get(namespace, {}).get(key, None)

    def set(
        self, namespace: bytes, key: bytes, value: bytes, ttl_seconds: float = 60
    ) -> None:
        with self._lock:
            namespace_cache = self._cache.get(namespace, {})
            namespace_cache[key] = value
            self._cache[namespace] = namespace_cache

            namespace_timers = self._ttl_timers.get(namespace, {})

            old_timer = namespace_timers.get(key, None)
            if old_timer is not None:
                old_timer.cancel()

            timer = threading.Timer(
                ttl_seconds, LocalTTLCache._delete, (self, namespace, key)
            )
            timer.daemon = True
            timer.start()

            namespace_timers[key] = timer
            self._ttl_timers[namespace] = namespace_timers

    def clear(self, namespace: bytes) -> None:
        with self._lock:
            self._cache.pop(namespace, None)

            namespace_timers = self._ttl_timers.get(namespace, {})
            for timer in namespace_timers.values():
                timer.cancel()

            self._ttl_timers.pop(namespace, None)

    def get_size(self, namespace: bytes) -> int:
        return len(self._ttl_timers.get(namespace, {}))

    def _delete(self, namespace: bytes, key: bytes) -> None:
        with self._lock:
            namespace_cache = self._cache.get(namespace, None)
            if namespace_cache is None:
                return

            namespace_cache.pop(key, None)
            if len(namespace_cache) == 0:
                del self._cache[namespace]
            else:
                self._cache[namespace] = namespace_cache


class AsyncLocalTTLCache(jwm._cache.ttl.cache.AsyncTTLCache):
    def __init__(self) -> None:
        self._cache: dict[bytes, dict[bytes, bytes]] = {}
        self._ttl_timers: dict[bytes, dict[bytes, asyncio.TimerHandle]] = {}
        self._lock = asyncio.Lock()

    async def get_size(self) -> int:
        return sum((len(values_) for values_ in self._ttl_timers.values()))

    async def get(self, namespace: bytes, key: bytes) -> bytes:
        return self._cache.get(namespace, {}).get(key, None)

    async def set(
        self, namespace: bytes, key: bytes, value: bytes, ttl_seconds: float = 60
    ) -> None:
        async with self._lock:
            namespace_cache = self._cache.get(namespace, {})
            namespace_cache[key] = value
            self._cache[namespace] = namespace_cache

            namespace_timers = self._ttl_timers.get(namespace, {})

            old_timer = namespace_timers.get(key, None)
            if old_timer is not None:
                old_timer.cancel()

            timer = asyncio.get_running_loop().call_later(
                ttl_seconds, LocalTTLCache._delete, (self, namespace, key)
            )

            namespace_timers[key] = timer
            self._ttl_timers[namespace] = namespace_timers

    async def clear(self, namespace: bytes) -> None:
        async with self._lock:
            self._cache.pop(namespace, None)

            namespace_timers = self._ttl_timers.get(namespace, {})
            for timer in namespace_timers.values():
                timer.cancel()

            self._ttl_timers.pop(namespace, None)

    def get_size(self, namespace: bytes) -> int:
        return len(self._ttl_timers.get(namespace, {}))

    async def _delete(self, namespace: bytes, key: bytes) -> None:
        async with self._lock:
            namespace_cache = self._cache.get(namespace, None)
            if namespace_cache is None:
                return

            namespace_cache.pop(key, None)
            if len(namespace_cache) == 0:
                del self._cache[namespace]
            else:
                self._cache[namespace] = namespace_cache
