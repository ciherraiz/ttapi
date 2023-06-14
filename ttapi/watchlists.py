from typing import Optional

import requests

from ttapi.instruments import InstrumentType
from ttapi.session import Session
from ttapi.models import JsonDataclass


class Pair(JsonDataclass):
    """
    Dataclass that represents a specific pair in a pairs watchlist.
    """
    left_action: str
    left_symbol: str
    left_quantity: int
    right_action: str
    right_symbol: str
    right_quantity: int


class PairsWatchlist(JsonDataclass):
    """
    Dataclass that represents a pairs watchlist object.
    """
    name: str
    order_index: int
    pairs_equations: list[Pair]

    @classmethod
    def get_pairs_watchlists(cls, session: Session) -> list['PairsWatchlist']:
        """
        Fetches a list of all Tastytrade public pairs watchlists.

        :param session: the session to use for the request.

        :return: a list of :class:`PairsWatchlist` objects.
        """
        response = session.request('GET', f'/pairs-watchlists')
        return [cls(**item) for item in response.data['data']['items']]

    @classmethod
    def get_pairs_watchlist(cls, session: Session, name: str) -> 'PairsWatchlist':
        """
        Fetches a Tastytrade public pairs watchlist by name.

        :param session: the session to use for the request.
        :param name: the name of the pairs watchlist to fetch.

        :return: a :class:`PairsWatchlist` object.
        """
        response = session.request('GET', f'/pairs-watchlists/{name}')
        return cls(**response.data['data'])

class Watchlist(JsonDataclass):
    """
    Dataclass that represents a watchlist object (public or private),
    with functions to update, publish, modify and remove watchlists.
    """
    name: str
    watchlist_entries: Optional[list[dict[str, str]]] = None
    group_name: str = 'default'
    order_index: int = 9999

    @classmethod
    def get_public_watchlists(cls, session: Session, counts_only: bool = False) -> list['Watchlist']:
        """
        Fetches a list of all Tastytrade public watchlists.

        :param session: the session to use for the request.
        :param counts_only: whether to only fetch the counts of the watchlists.

        :return: a list of :class:`Watchlist` objects.
        """
        payload={'counts-only': counts_only}
        response = session.request('GET', f'/public-watchlists', params=payload)
        return [cls(**item) for item in response.data['data']['items']]
        
    @classmethod
    def get_public_watchlist(cls, session: Session, name: str) -> 'Watchlist':
        """
        Fetches a Tastytrade public watchlist by name.

        :param session: the session to use for the request.
        :param name: the name of the watchlist to fetch.

        :return: a :class:`Watchlist` object.
        """
        response = session.request('GET', f'/pairs-watchlists/{name}')
        return cls(**response.data['data'])

    @classmethod
    def get_private_watchlists(cls, session: Session) -> list['Watchlist']:
        """
        Fetches a the user's private watchlists.

        :param session: the session to use for the request.

        :return: a list of :class:`Watchlist` objects.
        """
        response = session.request('GET', f'/watchlists')
        return [cls(**item) for item in response.data['data']['items']]

    @classmethod
    def get_private_watchlist(cls, session: Session, name: str) -> 'Watchlist':
        """
        Fetches a user's watchlist by name.

        :param session: the session to use for the request.
        :param name: the name of the watchlist to fetch.

        :return: a :class:`Watchlist` object.
        """
        response = session.request('GET', f'/watchlists/{name}')
        return cls(**response.data['data'])

    @classmethod
    def remove_private_watchlist(cls, session: Session, name: str) -> None:
        """
        Deletes the named private watchlist.

        :param session: the session to use for the request.
        :param name: the name of the watchlist to delete.
        """
        session.request('DELETE', f'/watchlists/{name}')

    def upload_private_watchlist(self, session: Session) -> None:
        """
        Creates a private remote watchlist identical to this local one.

        :param session: the session to use for the request.
        """
        session.request('POST', f'/watchlists', json=self.dict(by_alias=True))

    def update_private_watchlist(self, session: Session) -> None:
        """
        Updates the existing private remote watchlist.

        :param session: the session to use for the request.
        """
        session.request('PUT', f'/watchlists/{self.name}', json=self.dict(by_alias=True))

    def add_symbol(self, symbol: str, instrument_type: InstrumentType) -> None:
        """
        Adds a symbol to the watchlist.
        """
        if self.watchlist_entries is None:
            self.watchlist_entries = []
        self.watchlist_entries.append({'symbol': symbol, 'instrument-type': instrument_type})

    def remove_symbol(self, symbol: str, instrument_type: InstrumentType) -> None:
        """
        Removes a symbol from the watchlist.
        """
        if self.watchlist_entries is not None:
            self.watchlist_entries.remove({'symbol': symbol, 'instrument-type': instrument_type})