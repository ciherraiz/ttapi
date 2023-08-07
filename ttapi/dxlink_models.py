from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from ttapi.models import JsonDataclass

class EventType(Enum):
    """
    This is an :class:`~enum.Enum` that contains the valid subscription types for
    the quote streamer.

    Information on different types of events, their uses and their properties can be
    found at the `dxfeed Knowledge Base <https://kb.dxfeed.com/en/data-model/dxfeed-api-market-events.html>`_.
    """
    CANDLE = 'Candle'
    GREEKS = 'Greeks'
    PROFILE = 'Profile'
    QUOTE = 'Quote'
    SUMMARY = 'Summary'
    THEO_PRICE = 'TheoPrice'
    TIME_AND_SALE = 'TimeAndSale'
    TRADE = 'Trade'
    UNDERLYING = 'Underlying'

class ChannelState(Enum):
    SETUP = 'SETUP'
    AUTHORIZATION = 'AUTH_STATE'
    REQUEST = 'CHANNEL_REQUEST'
    OPENED = 'CHANNEL_OPENED'
    SUBSCRIPTION = 'FEED_SUBSCRIPTION'
    CONFIG = 'FEED_CONFIG'
    DATA = 'FEED_DATA'
    CANCEL = 'CHANNEL_CANCEL'

# Dataclasses from ws datastreamer.
# I cant't use Pydantic beacause I receive a lists of values. We need a mapping object to 
# use Pydantic (dictionnary)


class Event():
    @classmethod
    def from_stream(cls, data: list) -> list['Event']:
        """
        Takes a list of raw trade data fetched by :class:`~tastyworks.streamer.DataStreamer`
        and returns a list of :class:`~tastyworks.dxfeed.event.Event` objects.

        :param data: list of raw quote data from streamer

        :return: list of :class:`~tastyworks.dxfeed.event.Event` objects from data
        """
        objs = []
        size = len(cls.__dataclass_fields__)  # type: ignore
        multiples = len(data[0]) / size
        if not multiples.is_integer():
            raise Exception('Mapper data input values are not an integer multiple of the key size')
        for i in range(int(multiples)):
            offset = i * size
            local_values = data[0][offset:(i + 1) * size]
            objs.append(cls(*local_values))
        return objs


@dataclass
class Candle(Event):
    """
    A Candle event with open, high, low, close prices and other information
    for a specific period. Candles are build with a specified period using a
    specified price type with data taken from a specified exchange.
    """
    #: symbol of this event
    eventSymbol: str
    #: time of this event
    eventTime: int
    #: transactional event flags
    eventFlags: int
    #: unique per-symbol index of this candle event
    index: int
    #: timestamp of the candle in milliseconds
    time: int
    #: sequence number of this event
    sequence: int
    #: total number of events in the candle
    count: int
    #: the first (open) price of the candle
    open: float
    #: the maximal (high) price of the candle
    high: float
    #: the minimal (low) price of the candle
    low: float
    #: the last (close) price of the candle
    close: float
    #: the total volume of the candle
    volume: int
    #: volume-weighted average price
    vwap: float
    #: bid volume in the candle
    bidVolume: int
    #: ask volume in the candle
    askVolume: int
    #: implied volatility in the candle
    impVolatility: float
    #: open interest in the candle
    openInterest: int

@dataclass
class Greeks(Event):
    """
    Greek ratios, or simply Greeks, are differential values that show how the price of an option depends on other market parameters: on the price of the underlying asset, its volatility, etc. Greeks are used to assess the risks of customer portfolios. Greeks are derivatives of the value of securities in different axes. If a derivative is very far from zero, then the portfolio has a risky sensitivity in this parameter.
    """
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

@dataclass
class Profile(Event):
    """
    A Profile event provides the security instrument description. It represents the most recent information that is available about the traded security on the market at any given moment of time.
    """
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
    dividendFrequency: int
    #: the amount of the last paid dividend
    exDividendAmount: float
    #: identifier of the ex-dividend date
    exDividendDayId: int
    #: shares outstanding
    shares: int
    #: the number of shares that are available to the public for trade
    freeFloat: int

class Quote(JsonDataclass):
    """
    A Quote event is a snapshot of the best bid and ask prices, and other fields that change with each quote.
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
    bidSize: int
    #: time of the last ask change
    askTime: int
    #: ask exchange code
    askExchangeCode: str
    #: ask price
    askPrice: float
    #: ask size as integer number (rounded toward zero)
    askSize: int

@dataclass
class Summary(Event):
    """
    Summary is an information snapshot about the trading session including session highs, lows, etc. This record has two goals:

    1. Transmit OHLC values.

    2. Provide data for charting. OHLC is required for a daily chart, and if an exchange does not provide it, the charting services refer to the Summary event.

    Before opening the bidding, the values are reset to N/A or NaN.
    """
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

@dataclass
class TheoPrice(Event):
    """
    Theo price is a snapshot of the theoretical option price computation that is periodically performed by dxPrice model-free computation. dxFeed does not send recalculations for all options at the same time, so we provide you with a formula so you can perform calculations based on values from this event.
    """
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
    #: sequence number of this event to distinguish events that have the same time
    sequence: int
    #: theoretical price
    price: float
    #: underlying price at the time of theo price computation
    underlyingPrice: float
    #: delta of the theoretical price
    delta: float
    #: gamma of the theoretical price
    gamma: float
    #: implied simple dividend return of the corresponding option series
    dividend: float
    #: implied simple interest return of the corresponding option series
    interest: float

@dataclass
class TimeAndSale(Event):
    """
    TimeAndSale event represents a trade or other market event with a price, like
    market open/close price. TimeAndSale events are intended to provide information
    about trades in a continuous-time slice (unlike Trade events which are supposed
    to provide snapshots about the most recent trade). TimeAndSale events have a
    unique index that can be used for later correction/cancellation processing.
    """
    #: symbol of this event
    eventSymbol: str
    #: time of this event
    eventTime: int
    #: transactional event flags
    eventFlags: int
    #: unique per-symbol index of this time and sale event
    index: int
    #: timestamp of the original event
    time: int
    #: microseconds and nanoseconds part of time of the last bid or ask change
    timeNanoPart: int
    #: sequence of this quote
    sequence: int
    #: exchange code of this time and sale event
    exchangeCode: str
    #: price of this time and sale event
    price: float
    #: size of this time and sale event as integer number (rounded toward zero)
    size: int
    #: the current bid price on the market when this time and sale event had occured
    bidPrice: float
    #: the current ask price on the market when this time and sale event had occured
    askPrice: float
    #: sale conditions provided for this event by data feed
    exchangeSaleConditions: str
    #: transaction is concluded by exempting from compliance with some rule
    tradeThroughExempt: str
    #: initiator of the trade
    aggressorSide: str
    #: whether this transaction is a part of a multi-leg order
    spreadLeg: bool
    #: whether this transaction is completed during extended trading hours
    extendedTradingHours: bool
    #: normalized SaleCondition flag
    validTick: bool
    #: type of event - 0: new, 1: correction, 2: cancellation
    type: str
    #: Undocumented; always None
    buyer: None
    #: Undocumented; always None
    seller: None
    #: datetime of original event
    dtime: datetime = None

    def __post_init__(self):
        self.dtime = datetime.fromtimestamp(self.time/1000)
    

@dataclass
class Trade(Event):
    """
    A Trade event provides prices and the volume of the last transaction in regular trading hours, as well as the total amount per day in the number of securities and in their value. This event does not contain information about all transactions, but only about the last transaction for a single instrument.
    """
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
    dayVolume: int
    #: total turnover traded for a day
    dayTurnover: float
    #: tick direction of the last trade
    #: possible values are DOWN | UNDEFINED | UP | ZERO | ZERO_DOWN | ZERO_UP
    tickDirection: str
    #: whether the last trade was in extended trading hours
    extendedTradingHours: bool

@dataclass
class Underlying(Event):
    """
    Underlying event is a snapshot of computed values that are available for
    an option underlying symbol based on the option prices on the market. It
    represents the most recent information that is available about the
    corresponding values on the market at any given moment of time.
    """
    #: symbol of this event
    eventSymbol: str
    #: transactional event flags
    eventFlags: int
    #: unique per-symbol index of this event
    index: int
    #: timestamp of this event in milliseconds
    time: int
    #: sequence number of this event to distinguish events with the same time
    sequence: int
    #: 30-day implied volatility for this underlying based on VIX methodology
    volatility: float
    #: front month implied volatility for the underlying using VIX methodology
    frontVolatility: float
    #: back month implied volatility for the underlying using VIX methodology
    backVolatility: float
    #: call options traded volume for a day
    callVolume: int
    #: put options traded volume for a day
    putVolume: int
    #: options traded volume for a day
    optionVolume: int
    #: ratio of put options volume to call options volume for a day
    putCallRatio: float