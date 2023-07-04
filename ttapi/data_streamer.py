from abc import ABC
import asyncio
from asyncio import Queue, Lock
from datetime import datetime
import json
from dataclasses import dataclass
from typing import Optional, AsyncIterator
import aiohttp
from ttapi.exceptions import TastyTradeException
from ttapi.models import EventType, Channel, Event, Candle, Greeks, Profile, Quote, Summary, TheoPrice, TimeAndSale, Trade
from ttapi.session import Session
from dataclasses import dataclass
import websockets

class DataStreamer:
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
        #: The unique client identifier received from the server
        self.client_id: Optional[str] = None

        response = session.request('GET', '/quote-streamer-tokens')
        token_data = response.data['data']
        #logger.debug('response %s', token_data)
        self._auth_token = token_data['token']
        self._wss_url = (token_data['websocket-url'] + '/cometd').replace('https', 'wss')
        self._connect_task = asyncio.create_task(self._connect())

    @classmethod
    async def create(cls, session: Session) -> 'DataStreamer':
        """
        Factory method for the :class:`DataStreamer` object. Simply calls the
        constructor and performs the asynchronous setup tasks. This should be used
        instead of the constructor.

        Setup time is around 10-15 seconds.

        :param session: active user session to use
        """
        self = cls(session)
        while not self.client_id:
            await asyncio.sleep(0.1)

        return self

    async def _next_id(self):
        async with self._lock:
            self._counter += 1
        return self._counter

    async def _connect2(self) -> None:
        """
        Connect to the websocket server using the URL and authorization token provided
        during initialization.
        """
        headers = {'Authorization': f'{self._auth_token}'}

        # Connect to the websocket server
        async with websockets.connect(self._wss_url, extra_headers=headers) as websocket:  # type: ignore
            self._websocket = websocket
            await self._handshake()

            while not self.client_id:
                # Receive raw message from the websocket
                raw_message = await self._websocket.recv()
                message = json.loads(raw_message)[0]

                # Handshake phase
                if message['channel'] == Channel.HANDSHAKE:
                    #logger.debug('Handshake message: %s', message)
                    print(f'handshake answer: {message}')
                    if message['successful']:
                        self.client_id = message['clientId']
                        self._heartbeat_task = asyncio.create_task(self._heartbeat(10))
                    else:
                        raise TastyTradeException('Handshake failed')

            # Handshake finished
            # Main loop to handle incoming messages
            while True:
                # Receive raw message from the websocket
                raw_message = await self._websocket.recv()
                message = json.loads(raw_message)[0]
                #print(f"message {message['channel']}: {message}")

                # Process different message channels
                if message['channel'] == Channel.DATA:
                    #print('data received: %s', message)
                    #logger.debug('data received: %s', message)
                    await self._queue.put(message['data'])
                elif message['channel'] == Channel.CANDLE:
                    #print('candle received: %s', message)
                    #logger.debug('candle received: %s', message)
                    await self._queue_candle.put(message['data'])
                elif message['channel'] == Channel.SUBSCRIPTION:
                    #print('sub received: %s', message)
                    #logger.debug('sub received: %s', message)
                    pass

    async def _connect(self) -> None:
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

                while not self.client_id:
                    async for raw_msg in ws:
                    # Receive raw message from the websocket
                        #raw_msg = await self._websocket.recv()
                        message = json.loads(raw_msg.data)[0]

                        # Handshake phase
                        if message['channel'] == Channel.HANDSHAKE:
                            #logger.debug('Handshake message: %s', message)
                            print(f'handshake answer: {message}')
                            if message['successful']:
                                self.client_id = message['clientId']
                                self._heartbeat_task = asyncio.create_task(self._heartbeat(10))
                                break
                            else:
                                raise TastyTradeException('Handshake failed')

                # Handshake finished
                # Main loop to handle incoming messages
                while True:
                # Receive raw message from the websocket
                    async for raw_msg in ws:
                        #raw_message = await self._websocket.recv()
                        message = json.loads(raw_msg.data)[0]
                        print(f"message {message['channel']}: {message}")

                        # Process different message channels
                        if message['channel'] == Channel.DATA:
                            #print('data received: %s', message)
                            #logger.debug('data received: %s', message)
                            await self._queue.put(message['data'])
                        elif message['channel'] == Channel.CANDLE:
                            #print('candle received: %s', message)
                            #logger.debug('candle received: %s', message)
                            await self._queue_candle.put(message['data'])
                        elif message['channel'] == Channel.SUBSCRIPTION:
                            #print('sub received: %s', message)
                            #logger.debug('sub received: %s', message)
                            pass
    
    async def _handshake2(self) -> None:
        """
        Sends a handshake message to the specified WebSocket connection. The handshake
        message is sent as a JSON-encoded array with a single element, containing the
        handshake message as its only element.
        Token-Based-Authorization: 
        https://kb.dxfeed.com/en/data-access/token-based-authorization/establishing-connection.html
        """
        id = await self._next_id()
        message = {
            'id': id,
            'version': '1.0',
            'minimumVersion': '1.0',
            'channel': Channel.HANDSHAKE,
            'supportedConnectionTypes': ['websocket', 'long-polling', 'callback-polling'],
            'ext': {'com.devexperts.auth.AuthToken': self._auth_token},
            'advice': {
                'timeout': 60000,
                'interval': 0
            }
        }
        await self._websocket.send(json.dumps([message]))

    async def _handshake(self) -> None:
        """
        Sends a handshake message to the specified WebSocket connection. The handshake
        message is sent as a JSON-encoded array with a single element, containing the
        handshake message as its only element.
        Token-Based-Authorization: 
        https://kb.dxfeed.com/en/data-access/token-based-authorization/establishing-connection.html
        """
        id = await self._next_id()
        message = {
            'id': id,
            'version': '1.0',
            'minimumVersion': '1.0',
            'channel': Channel.HANDSHAKE,
            'supportedConnectionTypes': ['websocket', 'long-polling', 'callback-polling'],
            'ext': {'com.devexperts.auth.AuthToken': self._auth_token},
            'advice': {
                'timeout': 60000,
                'interval': 0
            }
        }
        await self._websocket.send_str(json.dumps([message]))
        #await self._websocket.send_json(message)

    async def listen(self) -> AsyncIterator[Event]:
        """
        Using the existing subscriptions, pulls :class:`~tastytrade.dxfeed.event.Event`s and yield returns
        them. Never exits unless there's an error or the channel is closed.
        """
        while True:
            raw_data = await self._queue.get()
            messages = self._map_message(raw_data)
            for message in messages:
                yield message

    async def listen_candle(self) -> AsyncIterator[Candle]:
        """
        Using the existing subscriptions, pulls candles and yield returns them.
        Never exits unless there's an error or the channel is closed.
        """
        while True:
            raw_data = await self._queue_candle.get()
            messages = self._map_message(raw_data)
            for message in messages:
                yield message  # type: ignore

    def close(self) -> None:
        """
        Closes the websocket connection and cancels the heartbeat task.
        """
        self._connect_task.cancel()
        self._heartbeat_task.cancel()

    async def _heartbeat(self, period=10) -> None:
        """
        After a Bayeux client has discovered the server’s capabilities with a handshake exchange, 
        a connection is established by sending a message to the /meta/connect channel.
        Sends a heartbeat message every 10 seconds to keep the connection alive.
        """
        while True:
            id = await self._next_id()
            message = {
                'id': id,
                'channel': Channel.HEARTBEAT,
                'clientId': self.client_id,
                'connectionType': 'websocket'
            }
            #logger.debug('sending heartbeat: %s', message)
            await self._websocket.send_str(json.dumps([message]))
            # send the heartbeat every period seconds
            await asyncio.sleep(period)

    async def subscribe(self, event_type: EventType, symbols: list[str], reset: bool = False) -> None:
        """
        Subscribes to quotes for given list of symbols. Used for recurring data feeds;
        if you just want to get a one-time quote, use :meth:`oneshot`.

        :param event_type: type of subscription to add
        :param symbols: list of symbols to subscribe for
        :param reset:
            whether to reset the subscription list (remove all other subscriptions of all types)
        """
        id = await self._next_id()
        message = {
            'id': id,
            'channel': Channel.SUBSCRIPTION,
            'data': {
                'reset': reset,
                'add': {event_type: symbols}
            },
            'clientId': self.client_id
        }
        #logger.debug('sending subscription: %s', message)
        await self._websocket.send_str(json.dumps([message]))

    async def unsubscribe(self, event_type: EventType, symbols: list[str]) -> None:
        """
        Removes existing subscription for given list of symbols.

        :param event_type: type of subscription to remove
        :param symbols: list of symbols to unsubscribe from
        """
        id = await self._next_id()
        message = {
            'id': id,
            'channel': Channel.SUBSCRIPTION,
            'data': {
                'reset': False,
                'remove': {event_type: symbols}
            },
            'clientId': self.client_id
        }
        #logger.debug('sending unsubscription: %s', message)
        await self._websocket.send_str(json.dumps([message]))

    async def subscribe_candle(self, ticker: str, start_time: datetime, interval: str) -> None:
        """
        Subscribes to candle-style 'OHLC' data for the given symbol.

        :param ticker: symbol to get date for
        :param start_time: starting time for the data range
        :param interval: the width of each candle in time, e.g. '5m', '1h', '3d', '1w', '1mo'
        """
        id = await self._next_id()
        message = {
            'id': id,
            'channel': Channel.SUBSCRIPTION,
            'data': {
                'addTimeSeries': {
                    'Candle': [{
                        'eventSymbol': f'{ticker}{{={interval}}}',
                        'fromTime': int(start_time.timestamp() * 1000)
                    }]
                }
            },
            'clientId': self.client_id
        }
        #logger.debug('sending subscription: %s', message)
        await self._websocket.send_str(json.dumps([message]))

    async def unsubscribe_candle(self, ticker: str, interval: str) -> None:
        """
        Removes existing :class:`~tastytrade.dxfeed.event.Candle` subscription for given list of symbols.

        :param ticker: symbol to unsubscribe from
        :param interval: candle width to unsubscribe from
        """
        id = await self._next_id()
        message = {
            'id': id,
            'channel': Channel.SUBSCRIPTION,
            'data': {
                'removeTimeSeries': {'Candle': [f'{ticker}{{={interval}}}']}
            },
            'clientId': self.client_id
        }
        #logger.debug('sending unsubscription: %s', message)
        await self._websocket.send_str(json.dumps([message]))

    def _map_message(self, message) -> list[Event]:
        """
        Takes the raw JSON data and returns a list of parsed :class:`~tastytrade.dxfeed.event.Event` objects.
        """
        # the first time around, types are shown
        if isinstance(message[0], str):
            msg_type = message[0]
        else:
            msg_type = message[0][0]
        # regardless, the second element will be the raw data
        data = message[1]

        # parse type or warn for unknown type
        if msg_type == EventType.CANDLE:
            return Candle.from_stream(data)
        elif msg_type == EventType.GREEKS:
            return Greeks.from_stream(data)
        elif msg_type == EventType.PROFILE:
            return Profile.from_stream(data)
        elif msg_type == EventType.QUOTE:
            return Quote.from_stream(data)
        elif msg_type == EventType.SUMMARY:
            return Summary.from_stream(data)
        elif msg_type == EventType.THEO_PRICE:
            return TheoPrice.from_stream(data)
        elif msg_type == EventType.TIME_AND_SALE:
            return TimeAndSale.from_stream(data)
        elif msg_type == EventType.TRADE:
            return Trade.from_stream(data)
        else:
            raise TastyTradeException(f'Unknown message type received from streamer: {message}')