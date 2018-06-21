import asyncio
import logging
from typing import TYPE_CHECKING

import aioredis
from aiohttp import ClientConnectorError, ClientOSError

from telegram_bot.bot import ExtendedBot
from telegram_bot.commands import init_commands
from telegram_bot.db import init_db
from telegram_bot.handlers import msg_broker_subscriber, queue_worker

if TYPE_CHECKING:
    from telegram_bot.config import Config

logger = logging.getLogger(__name__)


async def run_bot(bot):
    try:
        logger.info('Bot started.')
        await bot.loop()
    except ClientConnectorError:
        logger.exception('Bot connection can not be established.')
    except (ClientOSError, TimeoutError):
        logger.exception('Bot connection was dropped.')
    except Exception:
        logger.exception('Something awful.')
    finally:
        asyncio.get_event_loop().stop()


def main(cfg: 'Config'):
    event_loop = asyncio.get_event_loop()
    event_loop.set_debug(enabled=cfg.debug)

    db_pool = event_loop.run_until_complete(init_db(cfg.db_dsn))
    redis_sub = event_loop.run_until_complete(
        aioredis.create_redis(f'redis://{cfg.redis_host}:{cfg.redis_port}'))

    bot = ExtendedBot(db_pool=db_pool,
                      api_token=cfg.token, name='telegram_bot',
                      proxy=cfg.proxy, proxy_auth=cfg.proxy_auth)
    init_commands(bot)

    event_loop.create_task(run_bot(bot))
    event_loop.create_task(queue_worker(bot))
    event_loop.create_task(msg_broker_subscriber(bot, redis_sub))
    try:
        event_loop.run_forever()
    finally:
        logger.info('Closing loop')
        event_loop.stop()
        event_loop.close()
