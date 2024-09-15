# jwm.cache

## Python Caches inspired by the builtin `lru_cache` decorator

Provides python alternatives to `functools.lru_cache`, presently only supplies a Time To Live (TTL) version. 

The built in Last Recently Used (LRU) cache allows developers to cache function results via a decorator. It also supplies extra methods to query its initial parameters, present statistics and to clear its cache.

Provides a `ttl_cache` decorator with a similar signature to the `functools.lru_cache` including the extra methods. Rather than a cache size limit the `ttl_cache` provides a time to live parameter for each result.

## TTL cache extra features

The `ttl_cache` is written in pure python allowing it to be used in interpreters other than CPython (untested). It also offers the following extra features compared to `functools.lru_cache`:
 - Supports wrapping and caching async functions
 - Supports wrapping and caching methods
 - Wrappers are class instances rather than functions (avoids type hint gymnastics)
 - Supports default arguments being considered as part of the cache key
 - Uses a persistent hash function for creating cache keys (pythons default `hash` function as used by `functools.lru_cache` returns different hashes for different runs for security reasons).
   - You can implement the `__persistent_hash__` method to control how your object is hashed.
 - Optional identifier so multiple functions may share a cache
 - Allows custom cache to be used as a backend store
   - Provides an in memory backend cache that is used by default
   - Provides a Redis implementation to allow for a distributed shared cache
 - Allows custom serializers
   - Provides JSON and Pickle serializers with Pickle used as default
 - Supports mix and match async and sync functions with async and sync backend caches

## Usage

## Installation

Requires Python 3.10 or greater. Install from PyPi under the `jwm.cache` distribution.

```shell
pip install jwm.cache
```

Import into your program through the `jwm.cache` package.

```python
import jwm.cache
```

### Virtual Environment

It is highly recommended to install python projects into a virtual environment, see [PEP405](https://peps.python.org/pep-0405/) for motivations.

Create a virtual environment in the `.venv` directory.

```shell
python3 -m venv ./.venv
```

Activate with the correct command for your system.
```shell
# Linux/MacOS
. ./.venv/bin/activate
```

```shell
# Windows
.\.venv\Scripts\activate
```

### Installing from source

Make sure you have cloned the repository.

```shell
git clone https://github.com/jwmorley73/jwm.cache.git
```

Install the project using pip.

```shell
pip install .
```

If you want to include the developer tooling, add the `dev` optional dependencies.

```shell
pip install .[dev]
```
