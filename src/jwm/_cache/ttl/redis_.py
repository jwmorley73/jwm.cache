from __future__ import annotations

import datetime

try:
    import redis
    import redis.asyncio

    HAS_TTL_REDIS_CACHE = True
except ModuleNotFoundError:
    HAS_TTL_REDIS_CACHE = False

import jwm._cache.ttl.cache

if HAS_TTL_REDIS_CACHE:

    class RedisTTLCache(jwm._cache.ttl.cache.TTLCache):
        "Sync redis TTL Cache implementation."

        def __init__(self, client: redis.asyncio.Redis) -> None:
            """Redis Cache implementation.

            Args:
                redis (Redis): Redis client.
            """
            self.client = client

        @staticmethod
        def from_url(url: str) -> RedisTTLCache:
            """Create an RedisTTLCache from a redis server url.

            Args:
                url (str): Redis URL.

            Returns:
                RedisTTLCache: Created RedisTTLCache instance.
            """
            client = redis.from_url(url)
            return RedisTTLCache(client)

        def get(self, namespace: bytes, key: bytes) -> bytes | None:
            return self.client.get(namespace + key)

        def set(
            self, namespace: bytes, key: bytes, value: bytes, ttl_seconds: float = 60
        ) -> None:
            # Redis does not support ttl of zero
            if int(ttl_seconds * 1_000) == 0:
                self.client.delete(namespace + key)
                return

            self.client.set(namespace + key, value, px=int(ttl_seconds * 1_000))

        def clear(self, namespace: bytes) -> None:
            keys: list[bytes] = []
            cursor: int = 0
            while True:
                response: tuple[int, list[bytes]] = self.client.scan(
                    cursor=cursor,
                    match=namespace + b"*"
                )
                cursor, batch_keys = response

                keys.extend(batch_keys)
                
                if cursor == 0:
                    break

            if len(batch_keys) > 0:
                self.client.delete(*batch_keys)

        def get_size(self, namespace: bytes) -> int:
            count_: int = 0
            cursor: int = 0
            while True:
                response: tuple[int, list[bytes]] = self.client.scan(
                    cursor=cursor,
                    match=namespace + b"*"
                )
                cursor, batch_keys = response

                count_ += len(batch_keys)

                if cursor == 0:
                    break

            return count_

    class AsyncRedisTTLCache(jwm._cache.ttl.cache.AsyncTTLCache):
        "Async redis TTL Cache implementation."

        def __init__(self, client: redis.asyncio.Redis) -> None:
            """Redis Cache implementation.

            Args:
                redis (Redis): Async Redis client.
            """
            self.client = client

        @staticmethod
        def from_url(url: str) -> AsyncRedisTTLCache:
            """Create an AsyncRedisTTLCache from a redis server url.

            Args:
                url (str): Redis URL.

            Returns:
                AsyncRedisTTLCache: Created AsyncRedisTTLCache instance.
            """
            client = redis.asyncio.from_url(url)
            return AsyncRedisTTLCache(client)

        async def get(self, namespace: bytes, key: bytes) -> bytes | None:
            return await self.client.get(namespace + key)

        async def set(
            self, namespace: bytes, key: bytes, value: bytes, ttl_seconds: float = 60
        ) -> None:
            # Redis does not support ttl of zero
            if int(ttl_seconds * 1_000) == 0:
                await self.client.delete(namespace + key)
                return

            await self.client.set(namespace + key, value, px=int(ttl_seconds * 1_000))

        async def clear(self, namespace: bytes) -> None:
            keys: list[bytes] = []
            cursor: int = 0
            while True:
                response: tuple[int, list[bytes]] = await self.client.scan(
                    cursor=cursor,
                    match=namespace + b"*"
                )
                cursor, batch_keys = response

                keys.extend(batch_keys)

                if cursor == 0:
                    break

            if len(batch_keys) > 0:
                await self.client.delete(*batch_keys)

        async def get_size(self, namespace: bytes) -> int:
            count_: int = 0
            cursor: int = 0
            while True:
                response: tuple[int, list[bytes]] = await self.client.scan(
                    cursor=cursor,
                    match=namespace + b"*"
                )
                cursor, batch_keys = response

                count_ += len(batch_keys)
                
                if cursor == 0:
                    break

            return count_
