import json
import pickle
import typing


class Serializer(typing.Protocol):
    "Used to convert Python objects to and from a byte array."

    def serialize(self, value: typing.Any) -> bytes:
        """Convert value into an array of bytes.

        Args:
            value (Any): Python object to convert.

        Returns:
            bytes: Representation of python object in bytes.
        """

    def deserialize(self, obj: bytes) -> typing.Any:
        """Convert an array of bytes into a python object,

        Args:
            obj (bytes): Byte array representing a python object.

        Returns:
            Any: Python object from bytes.
        """


class PickleSerializer(Serializer):
    "Pickle implementation of Serializer."

    def __init__(
        self, protocol: int | None = None, *, fix_imports: bool = True
    ) -> None:
        """Creates a pickle serializer.

        For information on the provided arguments see the docstring for
        `pickle.dumps`.

        Args:
            protocol (int | None, optional): Pickling protocol. Defaults
                to None.
            fix_imports (bool, optional): Whether pickle should fix Python 2
                to Python 3 imports. Defaults to True.
        """
        self.protocol = protocol
        self.fixImports = fix_imports

    def serialize(self, obj: typing.Any) -> bytes:
        return pickle.dumps(
            obj,
            protocol=self.protocol,
            fix_imports=self.fixImports,
        )

    def deserialize(self, value: bytes) -> typing.Any:
        return pickle.loads(value, fix_imports=self.fixImports)


class JsonSerializer(Serializer):
    "JSON implementation of Serializer."

    def __init__(self, encoding: str = "utf-8") -> None:
        """Creates a JSON serializer.

        Args:
            encoding (str, optional): Encoding strings should use. Defaults to
            "utf-8".
        """
        self.encoding = encoding

    def serialize(self, obj: typing.Any) -> bytes:
        return json.dumps(obj).encode(self.encoding)

    def deserialize(self, value: bytes) -> typing.Any:
        return json.loads(value.decode(self.encoding))
