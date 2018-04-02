from typing import TYPE_CHECKING, NamedTuple, Dict, Any
import logging
import asyncio

import trafaret as t
import msgpack
from nats.aio.client import Client

if TYPE_CHECKING:
    from nats.aio.client import Msg

logger = logging.getLogger(__name__)


class Message(NamedTuple):
    subject: str
    data: Dict[str, Any]
    reply: str = None


class MsgBrokerClient:
    msg_schema_validator = t.Dict({
        t.Key('user'): t.Int(gte=0),
        t.Key('cmd'): t.String(),
        t.Key('data'): t.Type(dict),
        t.Key('priority', default=100): t.Int(gte=0)
    })

    def __init__(self, server_addr: str, service_name: str):
        self.server_addr = server_addr
        self.service_name = service_name
        self.client = Client()
        self.subscriber_queue = asyncio.Queue()

    async def run_client(self) -> None:
        await self.client.connect(servers=[f'nats://{self.server_addr}'], max_reconnect_attempts=-1)

    async def subscribe(self) -> int:
        return await self.client.subscribe_async(self.service_name, cb=self._handler)

    async def publish(self, receiver, msg: Dict[str, Any], reply=None) -> None:
        try:
            msg = self.pack_msg(msg)
        except t.DataError:
            logger.exception(f'Bad message: {msg}')
        else:
            if reply:
                # TODO: сделать проверку таймаута
                return await self.client.publish_request(receiver, reply, msg)
            else:
                asyncio.ensure_future(self.client.publish(receiver, msg))

    @classmethod
    def pack_msg(cls, data: Dict[str, Any]) -> bytes:
        data = cls.msg_schema_validator(data)
        return msgpack.packb(data)

    @classmethod
    def unpack_msg(cls, data: bytes) -> Dict[str, Any]:
        data = msgpack.unpackb(data, encoding='utf-8')
        logger.debug(f'Received message:{data}')
        return cls.msg_schema_validator(data)

    async def _handler(self, msg: 'Msg') -> None:
        try:
            subject = msg.subject
            reply = msg.reply
            data = self.unpack_msg(msg.data)
            msg = Message(subject, data, reply)
        except t.DataError:
            logger.exception(f'Bad message: {msg}')
        else:
            asyncio.ensure_future(self.subscriber_queue.put(msg))

    @property
    def is_connected(self) -> bool:
        return self.client.is_connected
