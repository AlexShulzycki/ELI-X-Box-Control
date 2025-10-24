import asyncio
from typing import Awaitable, Any


async def gather_and_flatten(awaitables: list[Awaitable[list[Any]]]) -> list[Any]:
    """
    Gathers a list of coroutines that each yeild a list, and then returns a flattened 1-d
    list of all the results
    :param awaitables: list of awaitable coroutines that each return a list
    :return: a flattened 1-d list of all the results
    """

    awaited: list[list[Any]] = await asyncio.gather(*awaitables)

    res: list[Any] = []
    for item in awaited:
        res.extend(item)
    return res
