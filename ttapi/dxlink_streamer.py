import asyncio
from asyncio import Queue
import json
import aiohttp
from typing import Optional, AsyncIterator, List, Dict
from ttapi import logger, cfg
from ttapi.exceptions import TastyTradeException
from ttapi.session import Session
from ttapi.dxlink_models import (ChannelState, EventType, Quote, Profile, Summary, Trade, 
                                 JsonDataclass)

# Even id channels
QUOTE_CH: int = 1
PROFILE_CH: int = 3
SUMMARY_CH: int = 5
TRADE_CH: int = 7
GREEKS_CH: int = 9

EVENTTYPE_CHANNEL: Dict = {EventType.QUOTE: QUOTE_CH,
                    EventType.PROFILE: PROFILE_CH,
                    EventType.SUMMARY: SUMMARY_CH,
                    EventType.TRADE: TRADE_CH}

class DXLinkStreamer:
    """
    A :class:`DataStreamer` object is used to fetch quotes or greeks for a given symbol
    or list of symbols. It should always be initialized using the :meth:`create` function,
    since the object cannot be fully instantiated without using async.

    """
    def __init__(self, session: Session):
        self._session: Session = session
        self._queue: Queue = Queue()
        
        self._keep_alive_timeout = cfg['dxlink']['keep_alive_timeout']
        self._proxy = cfg['network']['proxy'] if cfg['network'].get('proxy') else None

        self._channels = {QUOTE_CH: {'event': EventType.QUOTE, 'symbols': []},
                          PROFILE_CH: {'event': EventType.PROFILE, 'symbols': []},
                          SUMMARY_CH: {'event': EventType.SUMMARY, 'symbols': []},
                          TRADE_CH: {'event': EventType.TRADE, 'symbols': []},
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
        response = await self._session.request('GET', '/api-quote-tokens')
        self._token = response.data['data']['token']
        uri = response.data['data']['dxlink-url']

        # Connect to the websocket server
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(uri, proxy=self._proxy) as websocket:
                self._websocket = websocket
                await self._setup()
                # Main loop to handle incoming messages
                while True:
                    async for raw_msg in websocket:
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
                    #create channels
                    for event in EVENTTYPE_CHANNEL.keys():
                        await self._create_channel(event)
                    
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
    
    async def _create_channel(self, event: EventType) -> None:
        channel=EVENTTYPE_CHANNEL[event]
        self._channels[channel]['state'] = ChannelState.REQUEST

        message = {"type": ChannelState.REQUEST.value,
                    "channel": channel,
                    "service": "FEED",
                    "parameters": {"contract": "AUTO"}}
        await self._websocket.send_json(message)


    async def subscribe_event(self, event: EventType, symbols: List[str]) -> None:
        while self._channels[EVENTTYPE_CHANNEL[event]]['state'] == ChannelState.REQUEST:
            await asyncio.sleep(0)
         
        message = {"type": ChannelState.SUBSCRIPTION.value,
                    "channel": EVENTTYPE_CHANNEL[event],
                    "add": [{"symbol": symbol, "type": event.value} for symbol in symbols]}

        await self._websocket.send_json(message)

        self._channels[EVENTTYPE_CHANNEL[event]]['symbols'].extend(symbols)

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
    
    async def listen(self) -> AsyncIterator[JsonDataclass]:
        while True:
            data = await self._queue.get()
            yield data
    
    async def _map_message(self, message) -> None:
        """
        Takes the raw JSON data, parses the events and places them into their
        respective queues.

        :param message: raw JSON data from the websocket
        """

        # parse type or warn for unknown type
        data = message['data'][0]
        match data['eventType']:
            case EventType.QUOTE.value:
                event = Quote(**data)
            case EventType.PROFILE.value:
                event = Profile(**data)
            case EventType.SUMMARY.value:
                event = Summary(**data)
            case EventType.TRADE.value:
                event = Trade(**data)
        
        await self._queue.put(event)