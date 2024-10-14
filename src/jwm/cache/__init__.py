from __future__ import annotations

from jwm._cache.forward import *
from jwm._cache.hash_ import *
from jwm._cache.serializers import *
from jwm._cache.sync import *
from jwm._cache.ttl.cache import *
from jwm._cache.ttl.decorator import *
from jwm._cache.ttl.local import *
from jwm._cache.ttl.redis_ import *

__all__ = [
    "Serializer",
    "PickleSerializer",
    "JsonSerializer",
    "persistent_hash",
]

# Time To Live (TTL) Cache
__all__.extend(
    (
        "ttl_cache",
        "TTLDecorator",
        "TTLWrapper",
        "AsyncTTLWrapper",
        "TTLInfo",
        "TTLParameters",
        "TTLCache",
        "AsyncTTLCache",
        "LocalTTLCache",
        "AsyncLocalTTLCache",
        "set_default_ttl_cache",
        "get_default_ttl_cache",
    )
)
if HAS_TTL_REDIS_CACHE:
    __all__.extend(
        (
            "RedisTTLCache",
            "AsyncRedisTTLCache",
        )
    )
