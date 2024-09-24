import typing
import pickle

import jwm.cache

import pytest


@pytest.mark.parametrize(
    "value",
    (
        None,
        True,
        False,
        1,
        "2",
        b"3",
        (4, "5"),
        ["6", 7],
        {8, "9"},
        {10: "11", "12": 13}
    )
)
def test_pickle_serializer(value: typing.Any) -> None:
    serializer = jwm.cache.PickleSerializer()

    serialized = serializer.serialize(value)
    deserialized = serializer.deserialize(serialized)

    assert deserialized == value

@pytest.mark.parametrize(
    "value",
    (
        lambda x: x,
        (x for x in range(10))
    )
)
def test_pickle_serializer_fail(value: typing.Any) -> None:
    serializer = jwm.cache.PickleSerializer()

    with pytest.raises((pickle.PicklingError, TypeError)):
        serializer.serialize(value)


@pytest.mark.parametrize(
    "value",
    (
        None,
        True,
        False,
        1,
        "2",
        ["3", 4],
        {"5": "6", "7": 8}
    )
)
def test_json_serializer(value: typing.Any) -> None:
    serializer = jwm.cache.JsonSerializer()

    serialized = serializer.serialize(value)
    deserialized = serializer.deserialize(serialized)

    assert deserialized == value

@pytest.mark.parametrize(
    "value",
    (
        b"bytes",
        lambda x: x
    )
)
def test_json_serializer_fail(value: typing.Any) -> None:
    serializer = jwm.cache.JsonSerializer()

    with pytest.raises(TypeError):
        serializer.serialize(value)
