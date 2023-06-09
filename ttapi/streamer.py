import asyncio
from asyncio import Queue
import json
from typing import Any, Optional, Union, AsyncIterator
import websockets
from ttapi.session import Session
from ttapi.models import (JsonDataclass, QuoteAlert, UnderlyingYearGainSummary, 
                          InstrumentType, OrderChain, PlacedOrder, PriceEffect)
from ttapi.models import SubscriptionType

class AlertStreamer:
    """
    Used to subscribe to account-level updates (balances, orders, positions), public
    watchlist updates, quote alerts, and user-level messages. It should always be
    initialized using the :meth:`create` function, since the object cannot be fully
    instantiated without using async. 
    """

    def __init__(self, session: Session):
        # The token of active session is used to start the streamer
        self._token: str = session.token
        # Base wss url
        self._base_wss: str = session.wss
        
        self._queue: Queue = Queue()
        self._websocket = None

        self._connect_task = asyncio.create_task(self._connect())

    @classmethod
    async def create(cls, session: Session) -> 'AlertStreamer':
        """
        Factory method that performs the asynchronous setup tasks. This should be used
        instead of the constructor.
        """
        self = cls(session)
        while not self._websocket:
            await asyncio.sleep(0.1)
        return self
    
    async def _connect(self) -> None:
        """
        Connect to the websocket server using the URL and authorization token provided
        during initialization.
        """
        headers = {'Authorization': f'Bearer {self._token}'}
        async with websockets.connect(self._base_wss, extra_headers=headers) as websocket:
            self._websocket = websocket
            # Subscribes to HEARBEAT subscription
            self._heartbeat_task = asyncio.create_task(self._heartbeat())

            while True:
                raw_message = await self._websocket.recv()
                await self._queue.put(json.loads(raw_message))

    async def listen(self) -> AsyncIterator[JsonDataclass]:
        """
        Iterate over non-heartbeat messages received from the streamer,
        mapping them to their appropriate data class.
        """
        while True:
            data = await self._queue.get()
            type_str = data.get('type')
            if type_str is not None:
                yield self._map_message(type_str, data['data'])
            elif data.get('action') != 'heartbeat':
                print('subscription message: %s', data)
                #logger.debug('subscription message: %s', data) 

    def _map_message(self, type_str: str, data: dict) -> JsonDataclass:
        """
        I'm not sure what the user-status messages look like, so they're absent.
        """
        if type_str == 'AccountBalance':
            return AccountBalance(**data)
        elif type_str == 'CurrentPosition':
            return CurrentPosition(**data)
        elif type_str == 'Order':
            return PlacedOrder(**data)
        elif type_str == 'OrderChain':
            return OrderChain(**data)
        elif type_str == 'QuoteAlert':
            return QuoteAlert(**data)
        elif type_str == 'TradingStatus':
            return TradingStatus(**data)
        elif type_str == 'UnderlyingYearGainSummary':
            return UnderlyingYearGainSummary(**data)
        elif type_str == 'PublicWatchlists':
            return Watchlist(**data)
        else:
            raise TastytradeError(f'Unknown message type: {type_str}\n{data}')
                

    async def _heartbeat(self, period: int =10) -> None:
        """
        Sends a heartbeat message to keep the connection alive.
        """
        while not self._done:
            await self._subscribe(SubscriptionType.HEARTBEAT, '')
            # send the heartbeat every period seconds
            await asyncio.sleep(period)

    async def _subscribe(self, subscription: SubscriptionType, value: Union[Optional[str], list[str]] = '') -> None:
        """
        Subscribes to one of the :class:`SubscriptionType`s. Depending on the kind of
        subscription, the value parameter may be required.
        """
        message: dict[str, Any] = {
            'auth-token': self._token,
            'action': subscription
        }
        if value:
            message['value'] = value
        #logger.debug('sending alert subscription: %s', message)
        await self._websocket.send(json.dumps(message))  # type: ignore


    async def close(self) -> None:
        """
        Closes the websocket connection and cancels the heartbeat task.
        """
        self._connect_task.cancel()
        self._heartbeat_task.cancel()
    




