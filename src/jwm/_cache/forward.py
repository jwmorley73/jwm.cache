import typing

T = typing.TypeVar("T")


class ForwardDeclared(typing.Generic[T]):

    def __init__(self, *, initial_object: T | None = None) -> None:
        self.object = initial_object

    def set_object(self, cache: T) -> None:
        self.object = cache

    def __getattr__(self, name: str) -> typing.Any:
        if self.object is None:
            raise NotImplementedError("Object has yet to be set")

        return getattr(self.object, name)
