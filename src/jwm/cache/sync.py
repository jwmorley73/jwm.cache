from __future__ import annotations

import asyncio
import collections.abc
import concurrent.futures
import typing

T = typing.TypeVar("T")


# When calling coroutines within a sync wrapped function we run them in a new
# thread.
#
# We cannot use the existing thread incase there is an event loop already
# running. Also, we can't add the coroutine to an existing loop as we have no
# method of yielding control until the coroutine returns a result.
#
# This could likely be improved. Leaving as is for now.
def run_coroutine_in_thread(
    coroutine: collections.abc.Coroutine[typing.Any, typing.Any, T]
) -> T:
    """Runs and waits for coroutine to finish in its own thread.

    Args:
        coroutine (Coroutine[Any, Any, T]): Coroutine to run.

    Returns:
        T: Coroutine result.
    """
    with concurrent.futures.ThreadPoolExecutor(1) as executor:
        future = executor.submit(asyncio.run, coroutine)
        return future.result()
