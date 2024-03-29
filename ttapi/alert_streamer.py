import asyncio
from asyncio import Queue
import json
from typing import Any, Optional, Union, AsyncIterator
import aiohttp
#import websockets
from ttapi.config import logger
from ttapi.account import Account
from ttapi.session import Session
from ttapi.models import (JsonDataclass, Position, QuoteAlert, UnderlyingYearGainSummary, 
                          OrderChain, PlacedOrder, AccountBalance, TradingStatus, SubscriptionType)
from ttapi.watchlists import Watchlist
from ttapi.exceptions import TastyTradeException

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
        headers = {'Authorization': f'{self._token}'}
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(self._base_wss, headers=headers) as ws:
                self._websocket = ws
                # Subscribes to HEARBEAT subscription
                self._heartbeat_task = asyncio.create_task(self._heartbeat())

                while True:
                    # waiting for a new message
                    async for raw_msg in ws:
                        message = json.loads(raw_msg.data)
                        logger.debug(f'msg recv: {message}')
                        # add a json object to the queue
                        await self._queue.put(message)

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
                logger.debug(f'subs msg recv: {data}') 

    def _map_message(self, type_str: str, data: dict) -> JsonDataclass:

        if type_str == 'AccountBalance':
            return AccountBalance(**data)
        elif type_str == 'CurrentPosition':
            return Position(**data)
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
            raise TastyTradeException(f'Unknown message type: {type_str}\n{data}')
                
    async def account_subscribe(self, accounts: list[Account]) -> None:
        """
        Subscribes to account-level updates (balances, orders, positions).

        :param accounts: list of :class:`tastytrade.account.Account`s to subscribe to updates for
        """
        await self._subscribe(SubscriptionType.ACCOUNT, [acc.account_number for acc in accounts])

    async def public_watchlists_subscribe(self) -> None:
        """
        Subscribes to public watchlist updates.
        """
        await self._subscribe(SubscriptionType.PUBLIC_WATCHLISTS)

    async def quote_alerts_subscribe(self) -> None:
        """
        Subscribes to quote alerts (which are configured at a user level).
        """
        await self._subscribe(SubscriptionType.QUOTE_ALERTS)

    async def user_message_subscribe(self, session: Session) -> None:
        """
        Subscribes to user-level messages, e.g. new account creation.
        """
        await self._subscribe(SubscriptionType.USER_MESSAGE, value=session.external_id)

    async def _heartbeat(self, period: int =10) -> None:
        """
        Sends a heartbeat message to keep the connection alive.
        """
        while True:
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
        logger.debug(f'send subs: {message}')
        await self._websocket.send_str(json.dumps(message))  # type: ignore


    async def close(self) -> None:
        """
        Closes the websocket connection and cancels the heartbeat task.
        """
        self._connect_task.cancel()
        self._heartbeat_task.cancel()
    




