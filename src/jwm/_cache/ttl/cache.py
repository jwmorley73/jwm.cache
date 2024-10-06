import typing


class TTLCache(typing.Protocol):
    "Protocol for storing ttl_cache values."

    def get(self, namespace: bytes, key: bytes) -> bytes | None:
        """Get a value from the cache. If no value is found, returns None.

        Args:
            namespace (bytes): Namespace to search for key
            key (bytes): Key to search

        Returns:
            bytes | None: Value or None on miss
        """

    def set(
        self, namespace: bytes, key: bytes, value: bytes, ttl_seconds: float = 60
    ) -> None:
        """Sets a value in the cache with a time to live.

        Args:
            namespace (bytes): Key namespace
            key (bytes): Value key
            value (bytes): Value
            ttl_seconds (float, optional): Time to live in seconds.
                Defaults to 60.
        """

    def clear(self, namespace: bytes) -> None:
        """Clears all values in a namespace

        Args:
            namespace (bytes): Namespace to clear
        """

    def get_size(self, namespace: bytes) -> int:
        """Gets the number of set values in the namespace

        Args:
            namespace (bytes): Namespace to query

        Returns:
            int: Number of values
        """


class AsyncTTLCache(typing.Protocol):
    "Async protocol for storing ttl_cache values."

    async def get(self, namespace: bytes, key: bytes) -> bytes | None:
        """Get a value from the cache. If no value is found, returns None.

        Args:
            namespace (bytes): Namespace to search for key
            key (bytes): Key to search

        Returns:
            bytes | None: Value or None on miss
        """

    async def set(
        self, namespace: bytes, key: bytes, value: bytes, ttl_seconds: float = 60
    ) -> None:
        """Sets a value in the cache with a time to live.

        Args:
            namespace (bytes): Key namespace
            key (bytes): Value key
            value (bytes): Value
            ttl_seconds (float, optional): Time to live in seconds.
                Defaults to 60.
        """

    async def clear(self, namespace: bytes) -> None:
        """Clears all values in a namespace

        Args:
            namespace (bytes): Namespace to clear
        """

    async def get_size(self, namespace: bytes) -> int:
        """Gets the number of set values in the namespace

        Args:
            namespace (bytes): Namespace to query

        Returns:
            int: Number of values
        """
