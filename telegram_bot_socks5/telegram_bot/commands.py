import asyncio
from typing import TYPE_CHECKING

from telegram_bot import db

if TYPE_CHECKING:
    from telegram_bot.bot import ExtendedBot
    from aiotg.chat import Chat


async def cmd_start(chat: 'Chat', match: str):
    """/start command"""
    username = chat.message['from'].get('username')
    row = await db.get_user_id(username, chat.bot.db_pool)
    response = {'user_id': chat.id,
                'msg': ('Your telegram account is already linked '
                        'to the account on the '
                        '[123](http://123/)')}
    if not row:
        response['msg'] = ('You are not registered on the '
                           '[123](http://123/)')
        return asyncio.ensure_future(chat.bot.queue.put(response))
    user_id = row['telegram_user_id']
    if chat.id != user_id:
        await db.set_user_id(chat.id, username, chat.bot.db_pool)
        response['msg'] = ('Your telegram account now is linked '
                           'to the account on the '
                           '[123](http://123/)')
    return asyncio.ensure_future(chat.bot.queue.put(response))


def init_commands(bot: 'ExtendedBot'):
    bot.add_command(r'/start', cmd_start)
