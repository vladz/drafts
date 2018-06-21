import os
import logging
import json
from aiohttp import ClientSession

INN = os.environ['COMPANY_INN']
ADDR = os.environ['ADDR']
ATOL_LOGIN = os.environ['ATOL_LOGIN']
ATOL_PASSWORD = os.environ['ATOL_PASSWORD']
ATOL_GROUP = os.environ['ATOL_GROUP']

logger = logging.getLogger(__name__)


class AtolOnlineError(Exception):
    pass


class AtolOnlineTokenError(AtolOnlineError):
    pass


class AtolOnlineSendDocError(AtolOnlineError):
    pass


class AtolOnline:

    def __init__(self, token=None):
        self.token = token

    async def get_token(self):
        async with ClientSession() as session:
            resp = await session.post(
                'https://online.atol.ru/possystem/v3/getToken',
                json={'login': ATOL_LOGIN, 'pass': ATOL_PASSWORD})
            if resp.status == 200:
                resp_msg = await resp.text()
                msg = json.loads(resp_msg)
                self.token = msg.get('token')
                logger.debug(f'Atol-Online token: {self.token}')
            else:
                raise AtolOnlineTokenError('Can not get Atol-Online token.')

    async def post_sell(self, invoice, date, email, phone, items, amount):
        async with ClientSession() as session:
            data = {'external_id': invoice,
                    'timestamp': date.strftime('%d.%m.%Y %H:%M:%S'),
                    'service': {'inn': INN, 'payment_address': ADDR},
                    'receipt': {
                        'attributes': {'sno': 'osn', 'email': email,
                                       'phone': f'+{phone}'},
                        'items': items,
                        'payments': [{'type': 1, 'sum': amount}],
                        'total': amount}}
            resp = await session.post(
                f'https://online.atol.ru/possystem/v3/'
                f'{ATOL_GROUP}/sell?tokenid={self.token}',
                json=data)
            resp_msg = await resp.text()
            logger.debug(f'ATOL:{resp_msg}')
            if resp.status == 200:
                return resp_msg
            elif resp.status == 401:
                await self.get_token()
                await self.post_sell(invoice, date, email, phone, items,
                                     amount)
            else:
                raise AtolOnlineSendDocError('Can not send doc.')
