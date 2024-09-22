import builtins
import inspect
import sys
import types
import typing

MAX_HASH_MASK: int = pow(2, sys.hash_info.width) - 1
"Used to ensure hashed integers are within the systems size_t"


def djb2(obj: bytes) -> int:
    """Daniel J. Bernstein (DJB) v2 byte hashing algorithm taken and simplified
    from the Python source code.

    Args:
        obj (bytes): Object to hash.

    Returns:
        int: Hash of object.
    """
    hash_ = 5381
    for c in obj:
        hash_ = ((hash_ << 5) + hash_) + c

    return hash_


def siphash(obj: typing.Sequence[bytes]) -> int:
    """Sequence of bytes hashing algorithm taken and simplified from the
    python source code.

    Args:
        obj (Sequence[bytes]): Object to hash.

    Returns:
        int: Hash of object.
    """
    y = 0
    mult = 1000003
    x = 3430008
    for index, item in reversed(tuple(enumerate(obj))):
        y = item
        x = (x ^ y) * mult
        mult += 82520 + 2 * index

    x += 97531
    return x


def check_function(obj: typing.Any) -> bool:
    """Check if the object is a function.

    This is true for functions, lambdas, static methods, class methods
    and instance methods.

    This is false for anything else. Including objects with a __call__
    method.

    Args:
        obj (Any): Object to test.

    Returns:
        bool: Whether the Object is a function.
    """
    return hasattr(obj, "__call__") and hasattr(obj, "__qualname__")


def check_c_function(obj: typing.Any) -> bool:
    """Check if the object is a C function.

    This is True for C functions and C methods.

    Args:
        obj (Any): Object to test.

    Returns:
        bool: Whether the object is a C function.
    """
    return isinstance(obj, (types.BuiltinFunctionType, types.BuiltinMethodType))


INCOMPLETE = object()


def persistent_hash(
    obj: typing.Any,
    /,
    _history: typing.Optional[typing.Dict[int, int | typing.Any]] = None,
    _cyclers: typing.Optional[typing.List[int]] = None,
) -> int:
    """Hashes an object in a way that will be consistent between interpreter
    runs.

    Is more permissive than the standard library `hash` function. Will allow
    you to hash mutable primitives such as `list`, `set` and `dict`. Beware,
    this will lower the security of your application and could lead to
    unexpected collisions.

    The hash will be trimmed to your systems size_t.

    You can control what persistent hash your objects return through the
    `__persistent_hash__` method. This is highly recommended for objects as
    we have to heavily reduce their attributes by striping out anything written
    in c.

    Args:
        obj (Any): Object to hash

    Returns:
        int: The object hash trimmed to size_t.
    """
    global INCOMPLETE, MAX_HASH_MASK

    # Previous hashes found, used as a cache and to check for cycles
    if _history is None:
        _history = {}
    # Previous cycles found, used to keep cycle hash replacements consistent
    if _cyclers is None:
        _cyclers = []

    id_ = id(obj)
    miss = object()
    if (value := _history.get(id_, miss)) != miss:
        # Check is value already calculated
        if value != INCOMPLETE:
            return value

        # Cycle, return random number proportional to the cycle number
        cycler_factor = 873506627  # Something unusual
        try:
            return _cyclers.index(id_) * cycler_factor
        except ValueError:
            _cyclers.append(id_)
            return (len(_cyclers) - 1) * cycler_factor

    _history[id_] = INCOMPLETE

    hash_ = djb2
    collection_hash = siphash
    match type(obj):
        # We use the standard hash to ensure the same numbers of different
        # types have the same hash (Side effect is number hashes are persisted)
        case builtins.int:
            value = hash(obj) & MAX_HASH_MASK
        case builtins.float:
            value = hash(obj) & MAX_HASH_MASK
        case builtins.complex:
            value = hash(obj) & MAX_HASH_MASK
        case builtins.bool:
            value = hash(obj) & MAX_HASH_MASK
        case builtins.list:  # mutable hash
            value = (
                collection_hash(
                    tuple(
                        persistent_hash(item, _history=_history, _cyclers=_cyclers)
                        for item in obj
                    )
                )
                & MAX_HASH_MASK
            )
        case builtins.tuple:
            value = (
                collection_hash(
                    tuple(
                        persistent_hash(item, _history=_history, _cyclers=_cyclers)
                        for item in obj
                    )
                )
                & MAX_HASH_MASK
            )
        case builtins.range:
            value = persistent_hash(
                (obj.start, obj.stop, obj.step), _history=_history, _cyclers=_cyclers
            )
        case builtins.str:
            value = hash_(obj.encode("utf-8")) & MAX_HASH_MASK
        case builtins.bytes:
            value = hash_(obj) & MAX_HASH_MASK
        case builtins.bytearray:  # mutable hash
            value = (
                collection_hash(
                    tuple(
                        persistent_hash(item, _history=_history, _cyclers=_cyclers)
                        for item in obj
                    )
                )
                & MAX_HASH_MASK
            )
        case builtins.memoryview:
            value = (
                collection_hash(
                    tuple(
                        persistent_hash(item, _history=_history, _cyclers=_cyclers)
                        for item in obj
                    )
                )
                & MAX_HASH_MASK
            )
        case builtins.set:  # mutable hash
            value = (
                collection_hash(
                    tuple(
                        persistent_hash(item, _history=_history, _cyclers=_cyclers)
                        for item in obj
                    )
                )
                & MAX_HASH_MASK
            )
        case builtins.frozenset:
            value = (
                collection_hash(
                    tuple(
                        persistent_hash(item, _history=_history, _cyclers=_cyclers)
                        for item in obj
                    )
                )
                & MAX_HASH_MASK
            )
        case builtins.dict:  # mutable hash
            value = (
                collection_hash(
                    tuple(
                        persistent_hash(
                            (key, value), _history=_history, _cyclers=_cyclers
                        )
                        for key, value in obj.items()
                    )
                )
                & MAX_HASH_MASK
            )
        case builtins.type:
            value = persistent_hash(
                obj.__qualname__, _history=_history, _cyclers=_cyclers
            )
        case _:
            if hasattr(obj, "__persistent_hash__"):  # Implements __persistent_hash__
                value = obj.__persistent_hash__()
            elif obj is None:
                value = -776769781  # Something unusual
            elif check_function(obj):
                value = persistent_hash(
                    obj.__qualname__, _history=_history, _cyclers=_cyclers
                )
            else:  # Fallback, attempt to create a hash from the objects attributes
                attribute_names = dir(obj)
                attributes = tuple((a, getattr(obj, a)) for a in attribute_names)

                # Strip out attributes that are written in c (potentially a
                # different function on initial fetch, I assume python is using
                # some form of caching when crossing to c land and replaces the
                # original)
                attributes = tuple(a for a in attributes if not check_c_function(a[1]))

                return persistent_hash(attributes, _history=_history, _cyclers=_cyclers)

    _history[id_] = value
    return value


def hash_bound(
    bound: inspect.BoundArguments,
    *,
    typed: bool = False,
) -> int:
    """Creates a hash from supplied signature bound arguments.

    If typed is supplied and True the type is hashed alongside each value.

    A hashing algorithm other than the built in `hash` must be used. This is
    due to python guaranteeing different hashes each run for security in web
    contexts.

    Args:
        bound (BoundArguments): Signature bound arguments (from the `inspect`
            module).
        typed (bool, optional): Include types as part of the hash. Defaults to
            False.

    Returns:
        int: Hash of arguments. Size is dependent on the system size_t.
    """
    bound.apply_defaults()

    sorted_arguments = sorted(bound.arguments.items(), key=lambda item: item[0])

    if typed:
        object_ = tuple((key, type(value), value) for key, value in sorted_arguments)
    else:
        object_ = tuple((key, value) for key, value in sorted_arguments)

    return persistent_hash(object_)
