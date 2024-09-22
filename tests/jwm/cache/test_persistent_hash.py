import subprocess
import sys
import textwrap

import pytest

import jwm.cache


@pytest.mark.parametrize(
    "constructor, runs",
    (
        ("int(1)", 3),
        ("int(-1)", 3),
        ("float(2)", 3),
        ("float(-2)", 3),
        ("complex(3, 3)", 3),
        ("complex(-3, -3)", 3),
        ("True", 3),
        ("False", 3),
        ("[]", 3),
        ("[1, 2, 3]", 3),
        ("()", 3),
        ("(1, 2, 3)", 3),
        ("range(3)", 3),
        ("range(1, 3)", 3),
        ("range(3, 1, -1)", 3),
        ("''", 3),
        ("'string'", 3),
        ("b''", 3),
        ("b'bytes'", 3),
        ("bytearray(b'')", 3),
        ("bytearray(b'bytes')", 3),
        ("memoryview(b'')", 3),
        ("memoryview(b'bytes')", 3),
        ("set({})", 3),
        ("{1, 2, 3}", 3),
        ("frozenset({})", 3),
        ("frozenset({1, 2, 3})", 3),
        ("{}", 3),
        ("{1: 1, '2': '2', 3: '3'}", 3),
        ("str", 3),
        ("list", 3),
        ("None", 3),
        ("dir", 3),
        ("hash", 3),
    ),
)
def test_simple_persistent_hash(constructor: str, runs: int) -> None:
    processes: list[subprocess.CompletedProcess] = []
    for _ in range(runs):
        processes.append(
            subprocess.run(
                (
                    sys.executable,
                    "-c",
                    textwrap.dedent(
                        f"""
                            import jwm.cache;
                            obj = {constructor};
                            print(jwm.cache.persistent_hash(obj), end="")
                        """
                    ).replace("\n", ""),
                ),
                capture_output=True,
            )
        )

    first_hash = processes[0].stdout
    for process in processes:
        assert process.stdout == first_hash


class Bespoke:
    def __init__(self) -> None:
        foo: int = hash("bar")

    def __persistent_hash__(self) -> int:
        return 123456789


def test_dunder_persistent_hash() -> None:
    obj = Bespoke()

    hash_ = jwm.cache.persistent_hash(obj)
    assert hash_ == obj.__persistent_hash__()


def test_bespoke_persistent_hash() -> None:
    objects = tuple(Bespoke() for _ in range(3))

    first_hash = jwm.cache.persistent_hash(objects[0])
    for obj in objects:
        assert jwm.cache.persistent_hash(obj) == first_hash


class Automatic(list):
    FOO: str = "BAR"

    def __init__(self) -> None:
        foo: str = "bar"


def test_automatic_persistent_hash() -> None:
    objects = tuple(Automatic() for _ in range(3))

    first_hash = jwm.cache.persistent_hash(objects[0])
    for obj in objects:
        assert jwm.cache.persistent_hash(obj) == first_hash


def test_overflow_persistent_hash() -> None:
    max_Py_size_t = pow(2, sys.hash_info.width - 3)
    assert jwm.cache.persistent_hash(max_Py_size_t - 1) == 0
