from enum import Enum
from dataclasses import dataclass
from typing import Optional
from pydantic import validator
from datetime import datetime
from ttapi.models import JsonDataclass


class EventType(Enum):
    """
    This is an :class:`~enum.Enum` that contains the valid subscription types for
    the quote streamer.

    Information on different types of events, their uses and their properties can be
    found at the `dxfeed Knowledge Base <https://kb.dxfeed.com/en/data-model/dxfeed-api-market-events.html>`_.
    """
    GREEKS = 'Greeks'
    PROFILE = 'Profile'
    QUOTE = 'Quote'
    SUMMARY = 'Summary'
    TRADE = 'Trade'


class ChannelState(Enum):
    SETUP = 'SETUP'
    AUTHORIZATION = 'AUTH_STATE'
    REQUEST = 'CHANNEL_REQUEST'
    OPENED = 'CHANNEL_OPENED'
    SUBSCRIPTION = 'FEED_SUBSCRIPTION'
    CONFIG = 'FEED_CONFIG'
    DATA = 'FEED_DATA'
    CANCEL = 'CHANNEL_CANCEL'


class Greeks(JsonDataclass):
    """
    Greek ratios, or simply Greeks, are differential values that show how the price of an option depends on other market parameters: on the price of the underlying asset, its volatility, etc. Greeks are used to assess the risks of customer portfolios. Greeks are derivatives of the value of securities in different axes. If a derivative is very far from zero, then the portfolio has a risky sensitivity in this parameter.
    """
    #: type of event
    eventType: str
    #: symbol of this event
    eventSymbol: str
    #: time of this event
    eventTime: int
    #: transactional event flags
    eventFlags: int
    #: unique per-symbol index of this event
    index: int
    #: timestamp of this event in milliseconds
    time: int
    #: sequence number of thie event to distinguish events that have the same time
    sequence: int
    #: option market price
    price: float
    #: Black-Scholes implied volatility of the option
    volatility: float
    #: option delta
    delta: float
    #: option gamma
    gamma: float
    #: option theta
    theta: float
    #: option rho
    rho: float
    #: option vega
    vega: float

class Profile(JsonDataclass):
    """
    A Profile event provides the security instrument description. It represents the most recent information that is available about the traded security on the market at any given moment of time.
    """
    #: type of event
    eventType: str
    #: symbol of this event
    eventSymbol: str
    #: time of this event
    eventTime: int
    #: description of the security instrument
    description: str
    #: short sale restriction of the security instrument
    #: possible values are ACTIVE | INACTIVE | UNDEFINED
    shortSaleRestriction: str
    #: trading status of the security instrument
    #: possible values are ACTIVE | HALTED | UNDEFINED
    tradingStatus: str
    #: description of the reason that trading was halted
    statusReason: str
    #: starting time of the trading halt interval
    haltStartTime: int
    #: ending time of the trading halt interval
    haltEndTime: int
    #: maximal (high) allowed price
    highLimitPrice: float
    #: minimal (low) allowed price
    lowLimitPrice: float
    #: maximal (high) price in last 52 weeks
    high52WeekPrice: float
    #: minimal (low) price in last 52 weeks
    low52WeekPrice: float
    #: the correlation coefficient of the instrument to the S&P500 index
    beta: float
    #: earnings per share
    earningsPerShare: float
    #: Frequency of cash dividends payments per year (calculated)
    dividendFrequency: Optional[int]
    #: the amount of the last paid dividend
    exDividendAmount: float
    #: identifier of the ex-dividend date
    exDividendDayId: int
    #: shares outstanding
    shares: Optional[int]
    #: the number of shares that are available to the public for trade
    freeFloat: Optional[int]
    
    @validator('freeFloat', 'shares', 'dividendFrequency', pre=True)
    def nan_to_none(cls, v):
        if v == 'NaN':
            v = None
        return v

class Quote(JsonDataclass):
    """
    Quote event is a snapshot of the best bid and ask prices, and other fields that change with each quote. 
    It represents the most recent information that is available about the best quote on the market at any given moment of time.
    """
    #: type of event
    eventType: str
    #: symbol of this event
    eventSymbol: str
    #: time of this event
    eventTime: int
    #: sequence of this quote
    sequence: int
    #: microseconds and nanoseconds part of time of the last bid or ask change
    timeNanoPart: int
    #: time of the last bid change
    bidTime: int
    #: bid exchange code
    bidExchangeCode: str
    #: bid price
    bidPrice: float
    #: bid size as integer number (rounded toward zero)
    bidSize: Optional[int]
    #: time of the last ask change
    askTime: int
    #: ask exchange code
    askExchangeCode: str
    #: ask price
    askPrice: float
    #: ask size as integer number (rounded toward zero)
    askSize: Optional[int]

    @validator('bidSize', 'askSize', pre=True)
    def nan_to_none(cls, v):
        if v == 'NaN':
            v = None
        return v

class Summary(JsonDataclass):
    """
    Summary is an information snapshot about the trading session including session highs, lows, etc. This record has two goals:

    1. Transmit OHLC values.

    2. Provide data for charting. OHLC is required for a daily chart, and if an exchange does not provide it, the charting services refer to the Summary event.

    Before opening the bidding, the values are reset to N/A or NaN.
    """
    #: type of event
    eventType: str
    #: symbol of this event
    eventSymbol: str
    #: time of this event
    eventTime: int
    #: identifier of the day that this summary represents
    dayId: int
    #: the first (open) price for the day
    dayOpenPrice: float
    #: the maximal (high) price for the day
    dayHighPrice: float
    #: the minimal (low) price for the day
    dayLowPrice: float
    #: the last (close) price for the day
    dayClosePrice: float
    #: the price type of the last (close) price for the day
    #: possible values are FINAL | INDICATIVE | PRELIMINARY | REGULAR
    dayClosePriceType: str
    #: identifier of the previous day that this summary represents
    prevDayId: int
    #: the last (close) price for the previous day
    prevDayClosePrice: float
    #: the price type of the last (close) price for the previous day
    #: possible values are FINAL | INDICATIVE | PRELIMINARY | REGULAR
    prevDayClosePriceType: str
    #: total volume traded for the previous day
    prevDayVolume: float
    #: open interest of the symbol as the number of open contracts
    openInterest: int
    
class Trade(JsonDataclass):
    """
    A Trade event provides prices and the volume of the last transaction in regular trading hours, as well as the total amount per day in the number of securities and in their value. This event does not contain information about all transactions, but only about the last transaction for a single instrument.
    """
    #: type of event
    eventType: str
    #: symbol of this event
    eventSymbol: str
    #: time of this event
    eventTime: int
    #: time of the last trade
    time: int
    #: microseconds and nanoseconds time part of the last trade
    timeNanoPart: int
    #: sequence of the last trade
    sequence: int
    #: exchange code of the last trade
    exchangeCode: str
    #: price of the last trade
    price: float
    #: change of the last trade
    change: float
    #: size of the last trade as integer number (rounded toward zero)
    size: int
    #: identifier of the current trading day
    dayId: int
    #: total vlume traded for a day as integer number (rounded toward zero)
    dayVolume: Optional[int]
    #: total turnover traded for a day
    dayTurnover: float
    #: tick direction of the last trade
    #: possible values are DOWN | UNDEFINED | UP | ZERO | ZERO_DOWN | ZERO_UP
    tickDirection: str
    #: whether the last trade was in extended trading hours
    extendedTradingHours: bool

    @validator('dayVolume', pre=True)
    def nan_to_none(cls, v):
        if v == 'NaN':
            v = None
        return v