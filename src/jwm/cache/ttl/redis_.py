from __future__ import annotations

try:
    import redis
    import redis.asyncio

    HAS_TTL_REDIS_CACHE = True
except ModuleNotFoundError:
    HAS_TTL_REDIS_CACHE = False

import jwm.cache.ttl.cache

if HAS_TTL_REDIS_CACHE:

    class RedisTTLCache(jwm.cache.ttl.cache.TTLCache):
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
            self.client.set(namespace + key, value, ex=ttl_seconds)

        def clear(self, namespace: bytes) -> None:
            pipeline = self.client.pipeline()

            keys: list[bytes] = []
            cursor = 0
            while cursor != 0:
                cursor, batch_keys = pipeline.scan(
                    match=f"{namespace}*".encode("utf-8")
                )
                if batch_keys:
                    keys += batch_keys

            pipeline.delete(*batch_keys)

            pipeline.execute()

        def get_size(self, namespace: bytes) -> int:
            pipeline = self.client.pipeline()

            count_: int = 0
            cursor = 0
            while cursor != 0:
                cursor, batch_keys = pipeline.scan(
                    match=f"{namespace}*".encode("utf-8")
                )
                if batch_keys:
                    count_ += len(batch_keys)

            pipeline.execute()

            return count_

    class AsyncRedisTTLCache(jwm.cache.ttl.cache.AsyncTTLCache):
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
            await self.client.set(namespace + key, value, ex=ttl_seconds)

        async def clear(self, namespace: bytes) -> None:
            pipeline = self.client.pipeline()

            keys: list[bytes] = []
            cursor = 0
            while cursor != 0:
                cursor, batch_keys = pipeline.scan(
                    match=f"{namespace}*".encode("utf-8")
                )
                if batch_keys:
                    keys += batch_keys

            pipeline.delete(*batch_keys)

            await pipeline.execute()

        async def get_size(self, namespace: bytes) -> int:
            pipeline = self.client.pipeline()

            count_: int = 0
            cursor = 0
            while cursor != 0:
                cursor, batch_keys = pipeline.scan(
                    match=f"{namespace}*".encode("utf-8")
                )
                if batch_keys:
                    count_ += len(batch_keys)

            await pipeline.execute()

            return count_
