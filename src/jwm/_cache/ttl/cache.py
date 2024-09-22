import typing


class TTLCache(typing.Protocol):
    "Protocol for storing ttl_cache values."

    def get(self, namespace: bytes, key: bytes) -> bytes | None: ...

    def set(
        self, namespace: bytes, key: bytes, value: bytes, ttl_seconds: float = 60
    ) -> None: ...

    def clear(self, namespace: bytes) -> None: ...

    def get_size(self, namespace: bytes) -> int: ...


class AsyncTTLCache(typing.Protocol):
    "Async protocol for storing ttl_cache values."

    async def get(self, namespace: bytes, key: bytes) -> bytes | None: ...

    async def set(
        self, namespace: bytes, key: bytes, value: bytes, ttl_seconds: float = 60
    ) -> None: ...

    async def clear(self, namespace: bytes) -> None: ...

    async def get_size(self) -> int: ...
