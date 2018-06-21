import logging
import os
from typing import Union

import aiosocksy
from aiohttp import BasicAuth
from dataclasses import dataclass, InitVar

logger = logging.getLogger(__name__)

PROXY_SCHEMES = {'http', 'socks5'}

_proxy_auth_map = {'http': BasicAuth, 'socks5': aiosocksy.Socks5Auth}


class BadProxyScheme(Exception):
    pass


@dataclass
class Config:
    token: str
    name: str
    redis_host: str
    redis_port: int = 123
    db_dsn: str = None
    debug: bool = False
    proxy: str = None
    proxy_auth: Union['BasicAuth', 'aiosocksy.Socks5Auth'] = None

    db_host: InitVar[str] = None
    db_port: InitVar[Union[str, int]] = 123
    db_name: InitVar[str] = None
    db_user: InitVar[str] = None
    db_pwd: InitVar[str] = None
    proxy_scheme: InitVar[str] = 'http'
    proxy_host: InitVar[str] = None
    proxy_port: InitVar[Union[str, int]] = 123
    proxy_login: InitVar[str] = None
    proxy_pwd: InitVar[str] = None

    def __post_init__(self, db_host, db_port, db_name, db_user, db_pwd,
                      proxy_scheme, proxy_host, proxy_port,
                      proxy_login, proxy_pwd):
        self.db_dsn = (f'postgres://{db_user}:{db_pwd}@'
                       f'{db_host}:{db_port}/{db_name}')
        if not proxy_host:
            return
        if proxy_scheme not in PROXY_SCHEMES:
            raise BadProxyScheme(f'{proxy_scheme} not in proxy schemes, '
                                 f'use {PROXY_SCHEMES}')
        self.proxy = f'{proxy_scheme}://{proxy_host}:{proxy_port}'
        self.proxy_auth = _proxy_auth_map[proxy_scheme](login=proxy_login,
                                                        password=proxy_pwd)


def init(debug: bool) -> 'Config':
    cfg = Config(
        token=os.getenv('TELEGRAM_TOKEN'),
        name=os.getenv('APP_NAME', 'telegram_bot'),
        redis_host=os.getenv('REDIS_HOST', '123'),
        redis_port=os.getenv('REDIS_PORT', 123),
        debug=debug,
        db_host=os.getenv('DATABASE_HOST', '123'),
        db_port=os.getenv('DATABASE_PORT', 123),
        db_name=os.getenv('DATABASE_NAME', '123'),
        db_user=os.getenv('DATABASE_USER', '123'),
        db_pwd=os.getenv('DATABASE_PASSWORD', '123'),
        proxy_scheme=os.getenv('PROXY_SCHEME'),
        proxy_host=os.getenv('PROXY_HOST'),
        proxy_port=os.getenv('PROXY_PORT'),
        proxy_login=os.getenv('PROXY_LOGIN'),
        proxy_pwd=os.getenv('PROXY_PASSWORD')
    )
    return cfg
