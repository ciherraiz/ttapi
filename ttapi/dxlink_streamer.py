import asyncio
from asyncio import Queue, Lock
import json
import aiohttp
from typing import Optional, AsyncIterator
from ttapi.config import logger
from ttapi.exceptions import TastyTradeException
from ttapi.session import Session

class DXLinkStreamer:
    """
    A :class:`DataStreamer` object is used to fetch quotes or greeks for a given symbol
    or list of symbols. It should always be initialized using the :meth:`create` function,
    since the object cannot be fully instantiated without using async.

    """
    def __init__(self, session: Session):
        #: The active session used to initiate the streamer or make requests
        self.session: Session = session

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
        self._dxlink_token = response.data['data']['token']
        self._dxlink_url = response.data['data']['dxlink-url']

        #headers = {'Authorization': f'{self._dxlink_token}'}
        # Connect to the websocket server
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(self._dxlink_url, proxy=self.session.proxy) as ws:
                self._websocket = ws
                await self._setup()
                # Main loop to handle incoming messages
                while True:
                    async for raw_msg in ws:
                        message = json.loads(raw_msg.data)
                        logger.debug(f'message {message}')
                        self._authorized = True

    async def _setup(self) -> None:
        message = {"type": "SETUP", 
                   "channel": 0, 
                   "keepaliveTimeout": 60, 
                   "acceptKeepaliveTimeout": 60, 
                   "version": "0.1" }
        await self._websocket.send_json(message)

    
    async def _connect2(self) -> None:
        """
        Connect to the websocket server using the URL and authorization token provided
        during initialization.
        """
        headers = {'Authorization': f'{self._auth_token}'}

        # Connect to the websocket server
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(self._wss_url, headers=headers) as ws:
                self._websocket = ws
                await self._handshake()
                # Main loop to handle incoming messages
                while True:
                    async for raw_msg in ws:
                        # Receive raw message from the websocket
                        message = json.loads(raw_msg.data)[0]
                        logger.debug(f"message {message['channel']}: {message}")

                        if not self._handshake_done:
                            # Handshake phase
                            if message['channel'] == Channel.HANDSHAKE:
                                logger.debug(f'Handshake message: {message}')
                                if message['successful']:
                                    self.client_id = message['clientId']
                                    self._heartbeat_task = asyncio.create_task(self._heartbeat(10))
                                    self._handshake_done = True
                                    break
                                else:
                                    raise TastyTradeException('Handshake failed')
                        else:
                            # Process different message channels
                            if message['channel'] == Channel.DATA:
                                logger.debug(f'data received: {message}')
                                await self._queue.put(message['data'])
                            elif message['channel'] == Channel.CANDLE:
                                logger.debug(f'candle received: {message}')
                                await self._queue_candle.put(message['data'])
                            elif message['channel'] == Channel.SUBSCRIPTION:
                                logger.debug(f'subscription received: {message}')