import asyncio
from asyncio import Queue, Lock
import json
import aiohttp
from typing import Optional, AsyncIterator, List
from ttapi.config import logger
from ttapi.config import tastytrade as cfg
from ttapi.exceptions import TastyTradeException
from ttapi.session import Session
from ttapi.dxlink_models import ChannelState, EventType, Quote, JsonDataclass

# Channels id
QUOTE_CH = 1
PROFILE_CH = 2
SUMMARY_CH = 3
TRADE_CH = 4
GREEKS_CH = 5

class DXLinkStreamer:
    """
    A :class:`DataStreamer` object is used to fetch quotes or greeks for a given symbol
    or list of symbols. It should always be initialized using the :meth:`create` function,
    since the object cannot be fully instantiated without using async.

    """
    def __init__(self, session: Session):
        self._session: Session = session
        
        self._keep_alive_timeout = cfg['dxlink']['keep_alive_timeout']

        self._channels = {QUOTE_CH: {'event': EventType.QUOTE, 'queue': Queue()},
                          PROFILE_CH: {'event': EventType.PROFILE},
                          SUMMARY_CH: {'event': EventType.SUMMARY},
                          TRADE_CH: {'event': EventType.TRADE},
                          GREEKS_CH: {'event': EventType.GREEKS}}
        
        self._authorized: bool = False
        
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
        response = await self._session.tt_request('GET', '/api-quote-tokens')
        self._token = response.data['data']['token']
        uri = response.data['data']['dxlink-url']

        # Connect to the websocket server
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(uri, proxy=self._session.proxy) as ws:
                self._websocket = ws
                await self._setup()
                # Main loop to handle incoming messages
                while True:
                    async for raw_msg in ws:
                        message = json.loads(raw_msg.data)
                        await self._on_message(message)


    async def _setup(self) -> None:
        message = {"type": "SETUP", 
                   "channel": 0, 
                   "keepaliveTimeout": 60, 
                   "acceptKeepaliveTimeout": 60, 
                   "version": cfg['dxlink']['version'] }
        await self._websocket.send_json(message)
        
    async def _on_message(self, message_rcv) -> None:
        logger.debug(f'message {message_rcv}')
        message = None
        match message_rcv['type']:
            case ChannelState.SETUP.value:
                message = {"type": "AUTH",
                   "channel": 0,
                   "token": self._token}
            case ChannelState.AUTHORIZATION.value:
                if message_rcv['state'] == 'AUTHORIZED':
                    self._authorized = True
                    self._keep_alive_task = asyncio.create_task(self._keep_alive(self._keep_alive_timeout))
            case ChannelState.OPENED.value:
                self._channels[message_rcv['channel']]['state'] = ChannelState.OPENED
            case ChannelState.CONFIG.value:
                self._channels[message_rcv['channel']]['state'] = ChannelState.CONFIG
            case ChannelState.DATA.value:
                await self._map_message(message_rcv) 
                
        if message is not None:
            await self._websocket.send_json(message)

    async def _keep_alive(self, timeout: int = 10) -> None:
        message = {"type": "KEEPALIVE",
                   "channel": 0}
        while True:
            await self._websocket.send_json(message)
            await asyncio.sleep(timeout)
    
    async def subscribe_quote(self, symbol) -> None:
       
        # Create a new channel for quotes
        self._channels[QUOTE_CH]['state'] = ChannelState.REQUEST
        self._channels[QUOTE_CH]['symbol'] = symbol

        message = {"type": ChannelState.REQUEST.value,
                    "channel": 1,
                    "service": "FEED",
                    "parameters": {"contract": "AUTO"}}
        await self._websocket.send_json(message)

        while self._channels[QUOTE_CH]['state'] == ChannelState.REQUEST:
            await asyncio.sleep(0)

        message = {"type": ChannelState.SUBSCRIPTION.value,
                   "channel": QUOTE_CH,
                   "add": [{"symbol": symbol, "type": EventType.QUOTE.value}]}
        
        await self._websocket.send_json(message)

    async def close(self) -> None:
        """
        Closes the websocket connection and cancels the keep alive task.
        """
        # Close Channels
        for channel in self._channels.keys():
            message = {"type": ChannelState.CANCEL.value,
                       "channel": channel}
            await self._websocket.send_json(message)
        self._connect_task.cancel()
        self._keep_alive_task.cancel()

    
    async def listen_quotes(self) -> AsyncIterator[JsonDataclass]:
        while True:
            data = await self._channels[QUOTE_CH]['queue'].get()
            yield data

    
    async def _map_message(self, message) -> None:
        """
        Takes the raw JSON data, parses the events and places them into their
        respective queues.

        :param message: raw JSON data from the websocket
        """

        # parse type or warn for unknown type
        channel = message['channel']
        data = message['data'][0]
        match channel:
            case QUOTE_CH:
                event = Quote(**data)
                #data = Quote.from_stream(message['data'])
                
        
        await self._channels[channel]['queue'].put(event)