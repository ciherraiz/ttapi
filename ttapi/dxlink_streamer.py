import asyncio
from asyncio import Queue, Lock
import json
import aiohttp
from typing import Optional, AsyncIterator, List
from ttapi.config import logger
from ttapi.config import tastytrade as cfg
from ttapi.exceptions import TastyTradeException
from ttapi.session import Session
from ttapi.models import ChannelState, EventType

class DXLinkStreamer:
    """
    A :class:`DataStreamer` object is used to fetch quotes or greeks for a given symbol
    or list of symbols. It should always be initialized using the :meth:`create` function,
    since the object cannot be fully instantiated without using async.

    """
    def __init__(self, session: Session):
        #: The active session used to initiate the streamer or make requests
        self.session: Session = session
        self._channels = {}
        
        self._keep_alive_timeout = cfg['dxlink']['keep_alive_timeout']

        self._counter = 0
        self._lock: Lock = Lock()
        self._queue: Queue = Queue()
        self._queue_candle: Queue = Queue()
        
        self._authorized: bool = False
        #self._handshake_done = False
        
        self._connect_task = asyncio.create_task(self._connect())

    @classmethod
    async def create(cls, session: Session) -> 'DXLinkStreamer':
        """
        Factory method calls the
        constructor and performs the asynchronous setup tasks. This should be used
        instead of the constructor.
        """
        self = cls(session)
        while not self._authorized:
            await asyncio.sleep(0.1)

        return self
    
    async def _connect(self) -> None:
        """
        Connect to the websocket server using the URL and authorization token provided
        during initialization.
        """
        # Get DxLink API Quote Token
        # Quote streamer tokens are valid for 24 hours
        response = await self.session.tt_request('GET', '/api-quote-tokens')
        token = response.data['data']['token']
        url = response.data['data']['dxlink-url']

        # Connect to the websocket server
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(url, proxy=self.session.proxy) as ws:
                self._websocket = ws
                await self._setup()
                await self._authentication(token)
                # Main loop to handle incoming messages
                while True:
                    async for raw_msg in ws:
                        message = json.loads(raw_msg.data)
                        logger.debug(f'message {message}')
                        if not self._authorized:
                            if message['type'] == 'AUTH_STATE' and message['state'] == 'AUTHORIZED':
                                # the connection is authorized
                                self._authorized = True
                                # start connection maintenance by sendig keep alive message periodicaly
                                self._keep_alive_task = asyncio.create_task(self._keep_alive(self._keep_alive_timeout))
                            
                        if message['type'] == ChannelState.OPENED.value:
                            for key, values in self._channels.items():
                                if values['channel'] == message['channel']:
                                    self._channels[key]['state'] = ChannelState.OPENED
                                    break



    async def _setup(self) -> None:
        message = {"type": "SETUP", 
                   "channel": 0, 
                   "keepaliveTimeout": 60, 
                   "acceptKeepaliveTimeout": 60, 
                   "version": cfg['dxlink']['version'] }
        await self._websocket.send_json(message)

    async def _authentication(self, token) -> None:
        message = {"type": "AUTH",
                   "channel": 0,
                   "token": token}
        await self._websocket.send_json(message)

    async def _keep_alive(self, timeout: int = 10) -> None:
        message = {"type": "KEEPALIVE",
                   "channel": 0}
        while True:
            await self._websocket.send_json(message)
            await asyncio.sleep(timeout)
    
    async def subscribe_quote(self, symbol) -> None:
        if not self._channels.get(EventType.QUOTE):
            # Create a new channel for quotes
            self._channels[EventType.QUOTE] = {'channel': 1, 'state': ChannelState.REQUEST, 'symbol': symbol}
            message = {"type": ChannelState.REQUEST.value,
                       "channel": self._channels[EventType.QUOTE]['channel'],
                       "service": "FEED",
                       "parameters": {"contract": "AUTO"}}
            await self._websocket.send_json(message)

            while self._channels[EventType.QUOTE]['state'] == ChannelState.REQUEST:
                await asyncio.sleep(0)

        message = {"type": ChannelState.SUBSCRIPTION.value,
                   "channel": self._channels[EventType.QUOTE]['channel'],
                   "add": [{"symbol": symbol, "type": EventType.QUOTE.value}]}
        
        await self._websocket.send_json(message)

    async def close(self) -> None:
        """
        Closes the websocket connection and cancels the keep alive task.
        """
        # Close Channels
        for channel in self._channels.values():
            message = {"type": ChannelState.CANCEL.value,
                       "channel": channel['channel']}
            await self._websocket.send_json(message)
        self._connect_task.cancel()
        self._keep_alive_task.cancel()