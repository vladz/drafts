import asyncio
import logging
from json.decoder import JSONDecodeError
from typing import Any, Dict, TYPE_CHECKING

from telegram_bot.messages import msg_map

if TYPE_CHECKING:
    from telegram_bot.bot import ExtendedBot
    from aioredis import Redis

logger = logging.getLogger(__name__)


async def queue_worker(bot: 'ExtendedBot', delay=0.1):
    """Queue worker for message sending.
    Delay is required in order to prevent bot from being blocked."""
    while True:
        await asyncio.sleep(delay)
        item = await bot.queue.get()
        if item:
            try:
                bot.send_message(item['user_id'],
                                 item['msg'], parse_mode='Markdown')
            except KeyError as e:
                logger.exception(e)


async def prepare_notification(msg: Dict[str, Any]) -> Dict[str, Any]:
    user_id = msg['user_id']
    type = msg['type']
    args = msg['msg']
    m = msg_map[type](**args)
    return {'user_id': user_id, 'msg': str(m)}


async def msg_broker_subscriber(bot: 'ExtendedBot', sub: 'Redis'):
    """Subscriber to Redis channel."""
    ch, = await sub.subscribe('123')
    while await ch.wait_message():
        try:
            msg = await ch.get_json(encoding='utf-8')
            m = await prepare_notification(msg)
            asyncio.ensure_future(bot.queue.put(m))
        except (JSONDecodeError, KeyError, TypeError) as e:
            logger.exception(e)
