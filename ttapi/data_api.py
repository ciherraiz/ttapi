from datetime import datetime
from typing import Any, Optional, Dict, List
from ttapi.exceptions import TastyTradeException
from ttapi.models import EventType, Event, Greeks, Profile, Quote, Summary, TheoPrice, Trade, Underlying
from ttapi.session import Session
# https://kb.dxfeed.com/en/data-access/rest-api.html


class DataAPI():
    def __init__(self, 
                 session: Session):
        self._session = session

    async def get_event(self, 
                  event_type: EventType,
                  symbols: List[str],
                  start_time: Optional[datetime] = None,
                  end_time: Optional[datetime] = None):

        params: Dict[str, Any] = {
            'events': event_type,
            'symbols': ','.join(symbols)
        }

        if start_time is not None:
            params['fromTime'] = int(start_time.timestamp() * 1000)
        if end_time is not None:
            params['toTime'] = int(end_time.timestamp() * 1000)

        response = await self._session.dxf_request('GET', params=params)
        data = response.data[event_type]
        
        return [self._map_event(event_type, values) for _, values in data.item()]



    def _map_event(
        event_type: str,
        event_dict: Dict[str, Any]) -> Event:
        """
        Parses the raw JSON data from the dxfeed REST API into event objects.

        :param event_type: the type of event to map to
        :param event_dict: the raw JSON data from the dxfeed REST API
        """
        if event_type == EventType.GREEKS:
            return Greeks(**event_dict)
        elif event_type == EventType.PROFILE:
            return Profile(**event_dict)
        elif event_type == EventType.QUOTE:
            return Quote(**event_dict)
        elif event_type == EventType.SUMMARY:
            return Summary(**event_dict)
        elif event_type == EventType.THEO_PRICE:
            return TheoPrice(**event_dict)
        elif event_type == EventType.TRADE:
            return Trade(**event_dict)
        elif event_type == EventType.UNDERLYING:
            return Underlying(**event_dict[0])  # type: ignore
        else:
            raise TastyTradeException(f'Unknown event type: {event_type}')
