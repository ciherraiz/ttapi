from datetime import datetime, date
from decimal import Decimal
from typing import Optional, Any
from ttapi.models import (JsonDataclass, TradeableJsonDataclass, TickSize, OptionType, Deliverable, 
                          NestedOptionChainExpiration, InstrumentType, Roll, FutureMonthCode, 
                          FutureEtfEquivalent, NestedFutureOptionSubchain, NestedFutureOptionFuture,
                          QuantityDecimalPrecision)
from ttapi.session import Session

class Equity(TradeableJsonDataclass):
    """
    Dataclass that represents a Tastytrade equity object. Contains information
    about the equity and methods to populate that data using equity symbol(s).
    """
    id: int
    is_index: bool
    listed_market: str
    description: str
    lendability: str
    market_time_instrument_collection: str
    is_closing_only: bool
    is_options_closing_only: bool
    active: bool
    is_illiquid: bool
    is_etf: bool
    streamer_symbol: str
    borrow_rate: Optional[Decimal] = None
    cusip: Optional[str] = None
    short_description: Optional[str] = None
    halted_at: Optional[datetime] = None
    stops_trading_at: Optional[datetime] = None
    is_fractional_quantity_eligible: Optional[bool] = None
    tick_sizes: Optional[list[TickSize]] = None
    option_tick_sizes: Optional[list[TickSize]] = None

    @classmethod
    def get_active_equities(
        cls,
        session: Session,
        per_page: int = 1000,
        page_offset: Optional[int] = None,
        lendability: Optional[str] = None
    ) -> list['Equity']:
        """
        Returns a list of actively traded :class:`Equity` objects.

        :param session: the session to use for the request.
        :param per_page: the number of equities to get per page.
        :param page_offset: provide a specific page to get; if not provided, get all pages
        :param lendability: the lendability of the equities; 'Easy To Borrow', 'Locate Required', 'Preborrow'

        :return: a list of :class:`Equity` objects.
        """
        # if a specific page is provided, we just get that page;
        # otherwise, we loop through all pages
        paginate: bool = False
        if page_offset is None:
            page_offset = 0
            paginate = True

        payload: dict[str, Any] = {
            'per-page': per_page,
            'page-offset': page_offset,
            'lendability': lendability
        }

        #payload = {k: v for k,v in payload.items() if v is not None}
        
        equities = []
        while True:
            response = session.request('GET', f'/instruments/equities/active', params=payload)
            equities.extend([cls(**item) for item in response.data['data']['items']])
            
            pagination = response.data['pagination']
        
            if pagination['page-offset'] >= pagination['total-pages'] - 1: # finished
                break
            if not paginate:
                break
            
            payload['page-offset'] += 1

        return equities
    

    @classmethod
    def get_equities(
        cls,
        session: Session,
        symbols: Optional[list[str]] = None,
        lendability: Optional[str] = None,
        is_index: Optional[bool] = None,
        is_etf: Optional[bool] = None
    ) -> list['Equity']:
        """
        Returns a list of Equity objects from the given symbols.

        :param session: the session to use for the request.
        :param symbols: the symbols to get the equities for.
        :param lendability:
            the lendability of the equities; 'Easy To Borrow', 'Locate Required', 'Preborrow'
        :param is_index: whether the equities are indexes.
        :param is_etf: whether the equities are ETFs.

        :return: a list of Equity objects.
        """
        payload: dict[str, Any] = {
            'symbol[]': symbols,
            'lendability': lendability,
            'is-index': is_index,
            'is-etf': is_etf
        }
        payload={k: v for k, v in payload.items() if v is not None}
        response = session.request('GET', f'/instruments/equities', params=payload)

        return [cls(**item) for item in response.data['data']['items']]
    

    @classmethod
    def get_equity(cls, session: Session, symbol: str) -> 'Equity':
        """
        Returns a Equity object from the given symbol.

        :param session: the session to use for the request.
        :param symbol: the symbol to get the equity for.

        :return: a Equity object.
        """
        symbol = symbol.replace('/', '%2F')
        response = session.request('GET', f'/instruments/equities/{symbol}')
        return cls(**response.data['data'])
    
class Option(TradeableJsonDataclass):
    """
    Dataclass that represents a Tastytrade option object. Contains information
    about the option and methods to populate that data using option symbol(s).
    """
    active: bool
    strike_price: Decimal
    root_symbol: str
    underlying_symbol: str
    expiration_date: date
    exercise_style: str
    shares_per_contract: int
    option_type: OptionType
    option_chain_type: str
    expiration_type: str
    settlement_type: str
    stops_trading_at: datetime
    market_time_instrument_collection: str
    days_to_expiration: int
    expires_at: datetime
    is_closing_only: bool
    listed_market: Optional[str] = None
    halted_at: Optional[datetime] = None
    old_security_number: Optional[str] = None
    streamer_symbol: Optional[str] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.streamer_symbol:
            self._set_streamer_symbol()

    @classmethod
    def get_options(
        cls,
        session: Session,
        symbols: Optional[list[str]] = None,
        active: Optional[bool] = None,
        with_expired: Optional[bool] = None
    ) -> list['Option']:
        """
        Returns a list of `Option` objects from the given symbols.

        :param session: the session to use for the request.
        :param symbols: the OCC symbols to get the options for.
        :param active: whether the options are active.
        :param with_expired: whether to include expired options.

        :return: a list of :class:`Option` objects.
        """
        payload: dict[str, Any] = {
            'symbol[]': symbols,
            'active': active,
            'with-expired': with_expired
        }

        payload={k: v for k, v in payload.items() if v is not None}
        response = session.request('GET', f'/instruments/equity-options', params=payload)
        return [cls(**item) for item in response.data['data']['items']]

    @classmethod
    def get_option(
        cls,
        session: Session,
        symbol: str,
        active: Optional[bool] = None
    ) -> 'Option':
        """
        Returns a `Option` object from the given symbol.

        :param session: the session to use for the request.
        :param symbol: the symbol to get the option for, OCC format

        :return: a `Option` object.
        """
        symbol = symbol.replace('/', '%2F')
        payload = {'active': active} if active is not None else None
        response = session.request('GET', f'/instruments/equity-options/{symbol}', params=payload)
        return cls(**response.data['data'])
    
    def _set_streamer_symbol(self) -> None:
        if self.strike_price % 1 == 0:
            strike = '{0:.0f}'.format(self.strike_price)
        else:
            strike = '{0:.2f}'.format(self.strike_price)
            if strike[-1] == '0':
                strike = strike[:-1]

        exp = self.expiration_date.strftime('%y%m%d')
        self.streamer_symbol = \
            f".{self.underlying_symbol}{exp}{self.option_type.value}{strike}"
        
class NestedOptionChain(JsonDataclass):
    """
    Dataclass that represents a Tastytrade nested option chain object. Contains
    information about the option chain and a method to fetch one for a symbol.
    """
    underlying_symbol: str
    root_symbol: str
    option_chain_type: str
    shares_per_contract: int
    tick_sizes: list[TickSize]
    deliverables: list[Deliverable]
    expirations: list[NestedOptionChainExpiration]

    @classmethod
    def get_chain(cls, session: Session, symbol: str) -> 'NestedOptionChain':
        """
        Gets the option chain for the given symbol in nested format.

        :param session: the session to use for the request.
        :param symbol: the symbol to get the option chain for.

        :return: a :class:`NestedOptionChain` object.
        """
        symbol = symbol.replace('/', '%2F')
        response = session.request('GET', f'/option-chains/{symbol}/nested')
        return cls(**response.data['data']['items'][0])

class FutureProduct(JsonDataclass):
    """
    Dataclass that represents a Tastytrade future product object. Contains
    information about the future product and a method to fetch one for a symbol.

    Useful for fetching general information about a family of futures, without
    knowing the specific expirations or symbols.
    """
    root_symbol: str
    code: str
    description: str
    exchange: str
    product_type: str
    listed_months: list[FutureMonthCode]
    active_months: list[FutureMonthCode]
    notional_multiplier: Decimal
    tick_size: Decimal
    display_factor: Decimal
    streamer_exchange_code: str
    small_notional: bool
    back_month_first_calendar_symbol: bool
    first_notice: bool
    cash_settled: bool
    market_sector: str
    clearing_code: str
    clearing_exchange_code: str
    roll: Roll
    base_tick: Optional[int] = None
    sub_tick: Optional[int] = None
    contract_limit: Optional[int] = None
    product_subtype: Optional[str] = None
    security_group: Optional[str] = None
    true_underlying_code: Optional[str] = None
    clearport_code: Optional[str] = None
    legacy_code: Optional[str] = None
    legacy_exchange_code: Optional[str] = None
    option_products: Optional[list['FutureOptionProduct']] = None

    @classmethod
    def get_future_products(
        cls,
        session: Session
    ) -> list['FutureProduct']:
        """
        Returns a list of :class:`FutureProduct` objects available.

        :param session: the session to use for the request.

        :return: a list of :class:`FutureProduct` objects.
        """
        response = session.request('GET', f'/instruments/future-product')
        return [cls(**item) for item in response.data['data']]

    @classmethod
    def get_future_product(
        cls,
        session: Session,
        code: str,
        exchange: str = 'CME'
    ) -> 'FutureProduct':
        """
        Returns a :class:`FutureProduct` object from the given symbol.

        :param session: the session to use for the request.
        :param code: the product code, e.g. 'ES'
        :param exchange: the exchange to get the product from: 'CME', 'SMALLS', 'CFE', 'CBOED'

        :return: a :class:`FutureProduct` object.
        """
        code = code.replace('/', '')
        response = session.request('GET', f'/instruments/future-product/{exchange}/{code}')
        return cls(**response.data['data'])

        

class Future(TradeableJsonDataclass):
    """
    Dataclass that represents a Tastytrade future object. Contains information about
    the future and methods to fetch futures for symbol(s).
    """
    product_code: str
    tick_size: Decimal
    notional_multiplier: Decimal
    display_factor: Decimal
    last_trade_date: date
    expiration_date: date
    closing_only_date: date
    active: bool
    active_month: bool
    next_active_month: bool
    is_closing_only: bool
    stops_trading_at: datetime
    expires_at: datetime
    product_group: str
    exchange: str
    streamer_exchange_code: str
    streamer_symbol: Optional[str]
    back_month_first_calendar_symbol: bool
    is_tradeable: bool
    future_product: 'FutureProduct'
    instrument_type: InstrumentType = InstrumentType.FUTURE
    contract_size: Optional[Decimal] = None
    main_fraction: Optional[Decimal] = None
    sub_fraction: Optional[Decimal] = None
    first_notice_date: Optional[date] = None
    roll_target_symbol: Optional[str] = None
    true_underlying_symbol: Optional[str] = None
    future_etf_equivalent: Optional[FutureEtfEquivalent] = None
    tick_sizes: Optional[list[TickSize]] = None
    option_tick_sizes: Optional[list[TickSize]] = None
    spread_tick_sizes: Optional[list[TickSize]] = None

    @classmethod
    def get_futures(
        cls,
        session: Session,
        symbols: Optional[list[str]] = None,
        product_codes: Optional[list[str]] = None
    ) -> list['Future']:
        """
        Returns a list of :class:`Future` objects from the given symbols or product codes.

        :param session: the session to use for the request.
        :param symbols:
            symbols of the futures, e.g. 'ESZ9'. Leading forward slash is not required 
        :param product_codes:
            the product codes of the futures, e.g. 'ES', '6A'. Ignored if symbols are provided.

        :return: a list of :class:`Future` objects.
        """
        payload: dict[str, Any] = {
            'symbol[]': symbols,
            'product-code[]': product_codes
        }
        payload = {k: v for k, v in payload.items() if v is not None}

        response = session.request('GET', f'/instruments/futures', params=payload)
        return [cls(**item) for item in response.data['data']['items']]

    @classmethod
    def get_future(cls, session: Session, symbol: str) -> 'Future':
        """
        Returns a :class:`Future` object from the given symbol.

        :param session: the session to use for the request.
        :param symbol: the symbol to get the future for.

        :return: a :class:`Future` object.
        """
        symbol = symbol.replace('/', '')
        response = session.request('GET', f'/instruments/futures{symbol}')
        return cls(**response.data['data'])


class FutureOptionProduct(JsonDataclass):
    """
    Dataclass that represents a Tastytrade future option product object. Contains
    information about the future option product (deliverable for the future option).
    """
    root_symbol: str
    cash_settled: bool
    code: str
    display_factor: Decimal
    exchange: str
    product_type: str
    expiration_type: str
    settlement_delay_days: int
    market_sector: str
    clearing_code: str
    clearing_exchange_code: str
    clearing_price_multiplier: Decimal
    is_rollover: bool
    future_product: Optional['FutureProduct'] = None
    product_subtype: Optional[str] = None
    legacy_code: Optional[str] = None
    clearport_code: Optional[str] = None

    @classmethod
    def get_future_option_products(
        cls,
        session: Session
    ) -> list['FutureOptionProduct']:
        """
        Returns a list of :class:`FutureOptionProduct` objects available.

        :param session: the session to use for the request.

        :return: a list of :class:`FutureOptionProduct` objects.
        """
        response = session.request('GET', f'/instruments/future-option-products')
        return [cls(**item) for item in response.data['data']['items']]

    @classmethod
    def get_future_option_product(
        cls,
        session: Session,
        root_symbol: str,
        exchange: str = 'CME'
    ) -> 'FutureOptionProduct':
        """
        Returns a :class:`FutureOptionProduct` object from the given symbol.

        :param session: the session to use for the request.
        :param code: the root symbol of the future option
        :param exchange: the exchange to get the product from

        :return: a :class:`FutureOptionProduct` object.
        """
        root_symbol = root_symbol.replace('/', '')
        response = session.request('GET', f'/instruments/future-option-products/{exchange}/{root_symbol}')
        return cls(**response.data['data']['items'])
    
class FutureOption(TradeableJsonDataclass):
    """
    Dataclass that represents a Tastytrade future option object. Contains
    information about the future option, and methods to get future options.
    """
    underlying_symbol: str
    product_code: str
    expiration_date: date
    root_symbol: str
    option_root_symbol: str
    strike_price: Decimal
    exchange: str
    streamer_symbol: str
    option_type: OptionType
    exercise_style: str
    is_vanilla: bool
    is_primary_deliverable: bool
    future_price_ratio: Decimal
    multiplier: Decimal
    underlying_count: Decimal
    is_confirmed: bool
    notional_value: Decimal
    display_factor: Decimal
    settlement_type: str
    strike_factor: Decimal
    maturity_date: date
    is_exercisable_weekly: bool
    last_trade_time: str
    days_to_expiration: int
    is_closing_only: bool
    active: bool
    stops_trading_at: datetime
    expires_at: datetime
    exchange_symbol: str
    security_exchange: str
    sx_id: str
    instrument_type: InstrumentType = InstrumentType.FUTURE_OPTION
    future_option_product: Optional['FutureOptionProduct'] = None

    @classmethod
    def get_future_options(
        cls,
        session: Session,
        symbols: Optional[list[str]] = None,
        root_symbol: Optional[str] = None,
        expiration_date: Optional[date] = None,
        option_type: Optional[OptionType] = None,
        strike_price: Optional[Decimal] = None
    ) -> list['FutureOption']:
        """
        Returns a list of :class:`FutureOption` objects from the given symbols.

        NOTE: As far as I can tell, all of the parameters are bugged except for `symbols`.

        :param session: the session to use for the request.
        :param symbols: the Tastytrade symbols to filter by.
        :param root_symbol: the root symbol to get the future options for, e.g. 'EW3', 'SO'
        :param expiration_date: the expiration date for the future options.
        :param option_type: the option type to filter by.
        :param strike_price: the strike price to filter by.

        :return: a list of :class:`FutureOption` objects.
        """
        payload: dict[str, Any] = {
            'symbol[]': symbols,
            'option-root-symbol': root_symbol,
            'expiration-date': expiration_date,
            'option-type': option_type,
            'strike-price': strike_price
        }
        payload={k: v for k, v in payload.items() if v is not None}
        response = session.request('GET', f'/instruments/future-options', params=payload)
        return [cls(**item) for item in response.data['data']['items']]

    @classmethod
    def get_future_option(
        cls,
        session: Session,
        symbol: str
    ) -> 'FutureOption':
        """
        Returns a :class:`FutureOption` object from the given symbol.

        :param session: the session to use for the request.
        :param symbol: the symbol to get the option for, Tastytrade format

        :return: a :class:`FutureOption` object.
        """
        symbol = symbol.replace('/', '%2F').replace(' ', '%20')
        response = session.request('GET', f'/instruments/future-options/{symbol}')
        return cls(**response.data['data'])
    

class NestedFutureOptionChain(JsonDataclass):
    """
    Dataclass that represents a Tastytrade nested option chain object. Contains
    information about the option chain and a method to fetch one for a symbol.
    """
    futures: list[NestedFutureOptionFuture]
    option_chains: list[NestedFutureOptionSubchain]

    @classmethod
    def get_chain(cls, session: Session, symbol: str) -> 'NestedFutureOptionChain':
        """
        Gets the futures option chain for the given symbol in nested format.

        :param session: the session to use for the request.
        :param symbol: the symbol to get the option chain for.

        :return: a :class:`NestedFutureOptionChain` object.
        """
        symbol = symbol.replace('/', '')
        response = session.request('GET', f'/future-option-chains/{symbol}/nested')
        return cls(**response.data['data'])
       

class Warrant(JsonDataclass):
    """
    Dataclass that represents a Tastytrade warrant object. Contains
    information about the warrant, and methods to get warrants.
    """
    symbol: str
    instrument_type: InstrumentType
    listed_market: str
    description: str
    is_closing_only: bool
    active: bool
    cusip: Optional[str] = None

    @classmethod
    def get_warrants(
        cls,
        session: Session,
        symbols: Optional[list[str]] = None
    ) -> list['Warrant']:
        """
        Returns a list of :class:`Warrant` objects from the given symbols.

        :param session: the session to use for the request.
        :param symbols: symbols of the warrants, e.g. 'NKLAW'

        :return: a list of :class:`Warrant` objects.
        """
        payload = {'symbol[]': symbols} if symbols is not None else {}
        response = session.request('GET', f'/instruments/warrants', params=payload)
        return [cls(**item) for item in response.data['data']['items']]
        

    @classmethod
    def get_warrant(cls, session: Session, symbol: str) -> 'Warrant':
        """
        Returns a :class:`Warrant` object from the given symbol.

        :param session: the session to use for the request.
        :param symbol: the symbol to get the warrant for.

        :return: a :class:`Warrant` object.
        """
        response = session.request('GET', f'/instruments/warrants/{symbol}')
        return cls(**response.data['data'])


def get_quantity_decimal_precisions(session: Session) -> list[QuantityDecimalPrecision]:
    """
    Returns a list of :class:`QuantityDecimalPrecision` objects for different
    types of instruments.

    :param session: the session to use for the request.

    :return: a list of :class:`QuantityDecimalPrecision` objects.
    """

    response = session.request('GET', f'/instruments/quantity-decimal-precisions')
    return [QuantityDecimalPrecision(**item) for item in response.data['data']['items']]

