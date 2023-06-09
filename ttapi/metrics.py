from datetime import date
from typing import Any
from ttapi.models import (DividendInfo, EarningsInfo,  MarketMetricInfo)
from ttapi.session import Session


def get_market_metrics(session: Session, symbols: list[str]) -> list[MarketMetricInfo]:
    """
    Retrieves market metrics for the given symbols.

    :param session: active user session to use
    :param symbols: list of symbols to retrieve metrics for

    :return: a list of 'MarketMetricInfo' objects in JSON format.
    """
    payload = {'symbols': ','.join(symbols)}
    response = session.request('GET', f'/market-metrics', params=payload)
    return [MarketMetricInfo(**item) for item in response.data['data']['items']]


def get_dividends(session: Session, symbol: str) -> list[DividendInfo]:
    """
    Retrieves dividend information for the given symbol.

    :param session: active user session to use
    :param symbol: symbol to retrieve dividend information for

    :return: a list of Tastytrade 'DividendInfo' objects in JSON format.
    """
    symbol = symbol.replace('/', '%2F')
    response = session.request('GET', f'/market-metrics/historic-corporate-events/dividends/{symbol}')
    return [DividendInfo(**item) for item in response.data['data']['items']]
    


def get_earnings(session: Session, symbol: str, start_date: date) -> list[EarningsInfo]:
    """
    Retrieves earnings information for the given symbol.

    :param session: active user session to use
    :param symbol: symbol to retrieve earnings information for
    :param start_date: limits earnings to those on or after the given date

    :return: a list of Tastytrade 'EarningsInfo' objects in JSON format.
    """
    symbol = symbol.replace('/', '%2F')
    payload: dict[str, Any] = {'start-date': start_date}
    response = session.request('GET', f'/market-metrics/historic-corporate-events/earnings-reports/{symbol}', params=payload)
    return [EarningsInfo(**item) for item in response.data['data']['items']]
