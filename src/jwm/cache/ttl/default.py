import jwm.cache.forward
import jwm.cache.ttl.cache
import jwm.cache.ttl.local

DEFAULT_CACHE = jwm.cache.forward.ForwardDeclaredCache[
    jwm.cache.ttl.cache.TTLCache | jwm.cache.ttl.cache.AsyncTTLCache
](initial_cache=jwm.cache.ttl.local.LocalTTLCache())


def set_default_ttl_cache(
    cache: jwm.cache.ttl.cache.AsyncTTLCache | jwm.cache.ttl.cache.TTLCache,
) -> None:
    global DEFAULT_CACHE

    DEFAULT_CACHE.set_cache(cache)


def get_default_ttl_cache() -> (
    jwm.cache.ttl.cache.AsyncTTLCache | jwm.cache.ttl.cache.TTLCache
):
    global DEFAULT_CACHE

    return DEFAULT_CACHE.cache
