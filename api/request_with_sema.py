import logging
from typing import Any, Dict, TYPE_CHECKING

from aiohttp import ClientSession

from . import ExtApiError

if TYPE_CHECKING:
    import asyncio
    from aiohttp import web
    from settings import Config

logger = logging.getLogger(__name__)


async def api_request(url: str, data: Dict[str, Any],
                      app: 'web.Application') -> str:
    logger.debug(f'Ext request: {data}')
    cfg: 'Config' = app['config']
    semaphore: 'asyncio.Semaphore' = app['ext_api_semaphore']
    async with ClientSession(headers=cfg.ext_api.headers,
                             connector_owner=False,
                             conn_timeout=cfg.ext_api.conn_timeout,
                             read_timeout=cfg.ext_api.read_timeout) as session:
        async with semaphore, session.post(url=url, data=data) as resp:
            result = await resp.text()
            logger.debug(f'Ext response: {result}')
            if resp.status != 200:
                raise ExtApiError(result)
            return result
