import typing

T = typing.TypeVar("T")


class ForwardDeclaredCache(typing.Generic[T]):

    def __init__(self, *, initial_cache: T | None = None) -> None:
        self.cache = initial_cache

    def set_cache(self, cache: T) -> None:
        self.cache = cache

    def __getattr__(self, name: str) -> typing.Any:
        if self.cache is None:
            raise NotImplementedError("Cache has yet to be set")

        return getattr(self.cache, name)
