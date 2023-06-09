import asyncio
from asyncio import Queue
import json
from typing import Any, Optional, Union
import websockets
from ttapi.session import Session
from ttapi.streamer_models import SubscriptionType

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

        self._done = False
        
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

            while not self._done:
                raw_message = await self._websocket.recv()
                print(raw_message)
                await self._queue.put(json.loads(raw_message))
                

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
        self._done = True
        await asyncio.gather(self._connect_task, self._heartbeat_task)
    




