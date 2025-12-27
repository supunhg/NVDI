import asyncio
from typing import Any, Optional
import diskcache

from nvdi_cli.config.settings import Settings

_cache = diskcache.Cache(directory=".nvdi-cache")


async def cache_get(key: str) -> Optional[Any]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _cache.get, key)


async def cache_set(key: str, value: Any, ttl: int = None) -> None:
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _cache.set, key, value, ttl or Settings().cache_ttl)
