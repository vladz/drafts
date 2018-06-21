import asyncio
import logging

import aiohttp
from aiosocksy.connector import ProxyConnector, ProxyClientRequest
from aiotg import API_URL, Bot, BotApiError, RETRY_TIMEOUT, RETRY_CODES

try:
    import certifi
    import ssl
except ImportError:
    certifi = None

logger = logging.getLogger(__name__)


class ExtendedBot(Bot):
    def __init__(self, db_pool, proxy_auth=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.proxy_auth = proxy_auth
        self.request_class = aiohttp.ClientRequest
        self.db_pool = db_pool
        self.queue = asyncio.Queue()

    @property
    def session(self):
        if not self._session or self._session.closed:
            if certifi:
                context = ssl.create_default_context(cafile=certifi.where())
                connector = ProxyConnector(ssl_context=context)
            else:
                connector = ProxyConnector()

            self._session = aiohttp.ClientSession(
                connector=connector,
                request_class=ProxyClientRequest,
                json_serialize=self.json_serialize
            )
        return self._session

    async def _api_call(self, method, **params):
        url = "{0}/bot{1}/{2}".format(API_URL, self.api_token, method)
        logger.debug("api_call %s, %s", method, params)

        response = await self.session.post(url, data=params, proxy=self.proxy,
                                           proxy_auth=self.proxy_auth)

        if response.status == 200:
            return await response.json(loads=self.json_deserialize)
        elif response.status in RETRY_CODES:
            logger.info(
                "Server returned %d, retrying in %d sec.", response.status,
                RETRY_TIMEOUT
            )
            await response.release()
            await asyncio.sleep(RETRY_TIMEOUT)
            return await self.api_call(method, **params)
        else:
            if response.headers['content-type'] == 'application/json':
                json_resp = await response.json(loads=self.json_deserialize)
                err_msg = json_resp["description"]
            else:
                err_msg = await response.read()
            logger.error(err_msg)
            raise BotApiError(err_msg, response=response)

    def download_file(self, file_path, range=None):
        """
        Download a file from Telegram servers
        """
        headers = {"range": range} if range else None
        url = "{0}/file/bot{1}/{2}".format(API_URL, self.api_token, file_path)
        return self.session.get(url, headers=headers, proxy=self.proxy,
                                proxy_auth=self.proxy_auth)
