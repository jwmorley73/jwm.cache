import jwm._cache.forward
import jwm._cache.ttl.cache
import jwm._cache.ttl.local

DEFAULT_CACHE = jwm._cache.forward.ForwardDeclared[
    jwm._cache.ttl.cache.TTLCache | jwm._cache.ttl.cache.AsyncTTLCache
](initial_object=jwm._cache.ttl.local.LocalTTLCache())


def set_default_ttl_cache(
    cache: jwm._cache.ttl.cache.AsyncTTLCache | jwm._cache.ttl.cache.TTLCache,
) -> None:
    global DEFAULT_CACHE

    DEFAULT_CACHE.set_object(cache)


def get_default_ttl_cache() -> (
    jwm._cache.ttl.cache.AsyncTTLCache | jwm._cache.ttl.cache.TTLCache
):
    global DEFAULT_CACHE

    return DEFAULT_CACHE.object
