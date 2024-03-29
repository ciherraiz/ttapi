from abc import ABC
from datetime import date, datetime
from decimal import Decimal
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, validator

"""Dataclass for modeling a request reponse
"""
@dataclass
class RequestResult:
    status_code: int
    message: str = ''
    data: Dict = field(default_factory=lambda: {})

def _dasherize(s: str) -> str:
    """
    Converts a string from snake case to dasherized.

    :param s: string to convert

    :return: dasherized string
    """
    return s.replace('_', '-')

class JsonDataclass(BaseModel):
    """
    A pydantic dataclass that converts keys from snake case to dasherized (it automatically generates aliases)
    and performs type validation and coercion.
    """
    class Config:
        alias_generator = _dasherize
        populate_by_name = True


class TradingStatus(JsonDataclass):
    """
    Dataclass containing information about an account's trading status
    """
    account_number: str
    equities_margin_calculation_type: str
    fee_schedule_name: str
    futures_margin_rate_multiplier: Decimal
    has_intraday_equities_margin: bool
    id: int
    is_aggregated_at_clearing: bool
    is_closed: bool
    is_closing_only: bool
    is_cryptocurrency_enabled: bool
    is_frozen: bool
    is_full_equity_margin_required: bool
    is_futures_closing_only: bool
    is_futures_intra_day_enabled: bool
    is_futures_enabled: bool
    is_in_day_trade_equity_maintenance_call: bool
    is_in_margin_call: bool
    is_pattern_day_trader: bool
    is_portfolio_margin_enabled: bool
    is_risk_reducing_only: bool
    is_small_notional_futures_intra_day_enabled: bool
    is_roll_the_day_forward_enabled: bool
    are_far_otm_net_options_restricted: bool
    options_level: str
    short_calls_enabled: bool
    small_notional_futures_margin_rate_multiplier: Decimal
    is_equity_offering_enabled: bool
    is_equity_offering_closing_only: bool
    enhanced_fraud_safeguards_enabled_at: datetime
    updated_at: datetime
    day_trade_count: Optional[int] = None
    autotrade_account_type: Optional[str] = None
    clearing_account_number: Optional[str] = None
    clearing_aggregation_identifier: Optional[str] = None
    is_cryptocurrency_closing_only: Optional[bool] = None
    pdt_reset_on: Optional[date] = None
    cmta_override: Optional[int] = None

class PriceEffect(str, Enum):
    """
    Shows the sign of a price effect
    """
    CREDIT = 'Credit'
    DEBIT = 'Debit'
    NONE = 'None'

class AccountBalance(JsonDataclass):
    """
    Dataclass containing account balance information.
    """
    account_number: str
    cash_balance: Decimal
    long_equity_value: Decimal
    short_equity_value: Decimal
    long_derivative_value: Decimal
    short_derivative_value: Decimal
    long_futures_value: Decimal
    short_futures_value: Decimal
    long_futures_derivative_value: Decimal
    short_futures_derivative_value: Decimal
    long_margineable_value: Decimal
    short_margineable_value: Decimal
    margin_equity: Decimal
    equity_buying_power: Decimal
    derivative_buying_power: Decimal
    day_trading_buying_power: Decimal
    futures_margin_requirement: Decimal
    available_trading_funds: Decimal
    maintenance_requirement: Decimal
    maintenance_call_value: Decimal
    reg_t_call_value: Decimal
    day_trading_call_value: Decimal
    day_equity_call_value: Decimal
    net_liquidating_value: Decimal
    cash_available_to_withdraw: Decimal
    day_trade_excess: Decimal
    pending_cash: Decimal
    pending_cash_effect: PriceEffect
    long_cryptocurrency_value: Decimal
    short_cryptocurrency_value: Decimal
    cryptocurrency_margin_requirement: Decimal
    unsettled_cryptocurrency_fiat_amount: Decimal
    unsettled_cryptocurrency_fiat_effect: PriceEffect
    closed_loop_available_balance: Decimal
    equity_offering_margin_requirement: Decimal
    long_bond_value: Decimal
    bond_margin_requirement: Decimal
    snapshot_date: date
    time_of_day: Optional[str] = None
    reg_t_margin_requirement: Decimal
    futures_overnight_margin_requirement: Decimal
    futures_intraday_margin_requirement: Decimal
    maintenance_excess: Decimal
    pending_margin_interest: Decimal
    apex_starting_day_margin_equity: Optional[Decimal] = None
    buying_power_adjustment: Optional[Decimal] = None
    buying_power_adjustment_effect: Optional[PriceEffect] = None
    effective_cryptocurrency_buying_power: Decimal = None
    updated_at: datetime

class AccountBalanceSnapshot(JsonDataclass):
    """
    Dataclass containing account balance for a moment in time (snapshot).
    """
    account_number: str
    cash_balance: Decimal
    long_equity_value: Decimal
    short_equity_value: Decimal
    long_derivative_value: Decimal
    short_derivative_value: Decimal
    long_futures_value: Decimal
    short_futures_value: Decimal
    long_futures_derivative_value: Decimal
    short_futures_derivative_value: Decimal
    long_margineable_value: Decimal
    short_margineable_value: Decimal
    margin_equity: Decimal
    equity_buying_power: Decimal
    derivative_buying_power: Decimal
    day_trading_buying_power: Decimal
    futures_margin_requirement: Decimal
    available_trading_funds: Decimal
    maintenance_requirement: Decimal
    maintenance_call_value: Decimal
    reg_t_call_value: Decimal
    day_trading_call_value: Decimal
    day_equity_call_value: Decimal
    net_liquidating_value: Decimal
    cash_available_to_withdraw: Decimal
    day_trade_excess: Decimal
    pending_cash: Decimal
    pending_cash_effect: PriceEffect
    long_cryptocurrency_value: Decimal
    short_cryptocurrency_value: Decimal
    cryptocurrency_margin_requirement: Decimal
    unsettled_cryptocurrency_fiat_amount: Decimal
    unsettled_cryptocurrency_fiat_effect: PriceEffect
    closed_loop_available_balance: Decimal
    equity_offering_margin_requirement: Decimal
    long_bond_value: Decimal
    bond_margin_requirement: Decimal
    snapshot_date: date
    time_of_day: Optional[str] = None

class InstrumentType(str, Enum):
    """
    This is an :class:`~enum.Enum` that contains  types of instruments
    """
    BOND = 'Bond'
    CRYPTOCURRENCY = 'Cryptocurrency'
    CURRENCY_PAIR = 'Currency Pair'
    EQUITY = 'Equity'
    EQUITY_OFFERING = 'Equity Offering'
    EQUITY_OPTION = 'Equity Option'
    FUTURE = 'Future'
    FUTURE_OPTION = 'Future Option'
    INDEX = 'Index'
    UNKNOWN = 'Unknown'
    WARRANT = 'Warrant'

class Position(JsonDataclass):
    """
    Dataclass containing imformation about an individual position in a portfolio.
    """
    account_number: str
    symbol: str
    instrument_type: InstrumentType
    underlying_symbol: str
    quantity: Decimal
    quantity_direction: str
    close_price: Decimal
    average_open_price: Decimal
    average_yearly_market_close_price: Decimal
    average_daily_market_close_price: Decimal
    multiplier: int
    cost_effect: str
    is_suppressed: bool
    is_frozen: bool
    realized_day_gain: Decimal
    realized_day_gain_effect: PriceEffect
    realized_day_gain_date: date
    realized_today: Decimal
    realized_today_effect: PriceEffect
    realized_today_date: date
    created_at: datetime
    updated_at: datetime
    mark: Optional[Decimal] = None
    mark_price: Optional[Decimal] = None
    restricted_quantity: Optional[Decimal] = None
    expires_at: Optional[datetime] = None
    fixing_price: Optional[Decimal] = None
    deliverable_type: Optional[str] = None
    average_yearly_market_close_price: Optional[Decimal] = None
    average_daily_market_close_price: Optional[Decimal] = None
    realized_day_gain_effect: Optional[PriceEffect] = None
    realized_day_gain_date: Optional[date] = None
    realized_today_effect: Optional[PriceEffect] = None
    realized_today_date: Optional[date] = None

class Lot(JsonDataclass):
    """
    Dataclass containing information about the lot of a position.
    """
    id: str
    transaction_id: int
    quantity: Decimal
    price: Decimal
    quantity_direction: str
    executed_at: datetime
    transaction_date: date

class Transaction(JsonDataclass):
    """
    Dataclass containing information about a past transaction.
    """
    id: int
    account_number: str
    transaction_type: str
    transaction_sub_type: str
    description: str
    executed_at: datetime
    transaction_date: date
    value: Decimal
    value_effect: PriceEffect
    net_value: Decimal
    net_value_effect: PriceEffect
    is_estimated_fee: bool
    symbol: Optional[str] = None
    instrument_type: Optional[InstrumentType] = None
    underlying_symbol: Optional[str] = None
    action: Optional[str] = None
    quantity: Optional[Decimal] = None
    price: Optional[Decimal] = None
    regulatory_fees: Optional[Decimal] = None
    regulatory_fees_effect: Optional[PriceEffect] = None
    clearing_fees: Optional[Decimal] = None
    clearing_fees_effect: Optional[PriceEffect] = None
    commission: Optional[Decimal] = None
    commission_effect: Optional[PriceEffect] = None
    proprietary_index_option_fees: Optional[Decimal] = None
    proprietary_index_option_fees_effect: Optional[PriceEffect] = None
    ext_exchange_order_number: Optional[str] = None
    ext_global_order_number: Optional[int] = None
    ext_group_id: Optional[str] = None
    ext_group_fill_id: Optional[str] = None
    ext_exec_id: Optional[str] = None
    exec_id: Optional[str] = None
    exchange: Optional[str] = None
    order_id: Optional[int] = None
    exchange_affiliation_identifier: Optional[str] = None
    leg_count: Optional[int] = None
    destination_venue: Optional[str] = None
    other_charge: Optional[Decimal] = None
    other_charge_effect: Optional[PriceEffect] = None
    other_charge_description: Optional[str] = None
    reverses_id: Optional[int] = None
    cost_basis_reconciliation_date: Optional[date] = None
    lots: Optional[list[Lot]] = None
    agency_price: Optional[Decimal] = None
    principal_price: Optional[Decimal] = None

class NetLiquidation(JsonDataclass):
    """
    Dataclass containing historical net liquidation data in OHLC format
    """
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    pending_cash_open: Decimal
    pending_cash_high: Decimal
    pending_cash_low: Decimal
    pending_cash_close: Decimal
    total_open: Decimal
    total_high: Decimal
    total_low: Decimal
    total_close: Decimal
    time: datetime

class PositionLimit(JsonDataclass):
    """
    Dataclass containing information about general account limits.
    """
    account_number: str
    equity_order_size: int
    equity_option_order_size: int
    future_order_size: int
    future_option_order_size: int
    underlying_opening_order_limit: int
    equity_position_size: int
    equity_option_position_size: int
    future_position_size: int
    future_option_position_size: int

class MarginRequirement(JsonDataclass):
    """
    Dataclass containing general margin requirement information for a symbol.
    """
    underlying_symbol: str
    long_equity_initial: Decimal
    short_equity_initial: Decimal
    long_equity_maintenance: Decimal
    short_equity_maintenance: Decimal
    naked_option_standard: Decimal
    naked_option_minimum: Decimal
    naked_option_floor: Decimal
    clearing_identifier: Optional[str] = None
    is_deleted: Optional[bool] = None

class MarginReportEntry(JsonDataclass):
    """
    Dataclass containing an individual entry (relating to a specific position)
    as part of the overall margin report.
    """
    description: str
    code: str
    underlying_symbol: str
    underlying_type: str
    expected_price_range_up_percent: Decimal
    expected_price_range_down_percent: Decimal
    point_of_no_return_percent: Decimal
    margin_calculation_type: str
    margin_requirement: Decimal
    margin_requirement_effect: PriceEffect
    initial_requirement: Decimal
    initial_requirement_effect: PriceEffect
    maintenance_requirement: Decimal
    maintenance_requirement_effect: PriceEffect
    buying_power: Decimal
    buying_power_effect: PriceEffect
    groups: list[dict[str, Any]]
    price_increase_percent: Decimal
    price_decrease_percent: Decimal


class MarginReport(JsonDataclass):
    """
    Dataclass containing an overall portfolio margin report.
    """
    account_number: str
    description: str
    margin_calculation_type: str
    option_level: str
    margin_requirement: Decimal
    margin_requirement_effect: PriceEffect
    maintenance_requirement: Decimal
    maintenance_requirement_effect: PriceEffect
    margin_equity: Decimal
    margin_equity_effect: PriceEffect
    option_buying_power: Decimal
    option_buying_power_effect: PriceEffect
    reg_t_margin_requirement: Decimal
    reg_t_margin_requirement_effect: PriceEffect
    reg_t_option_buying_power: Decimal
    reg_t_option_buying_power_effect: PriceEffect
    maintenance_excess: Decimal
    maintenance_excess_effect: PriceEffect
    groups: list[MarginReportEntry]
    last_state_timestamp: int
    initial_requirement: Optional[Decimal] = None
    initial_requirement_effect: Optional[PriceEffect] = None


class OrderType(str, Enum):
    """
    This is an :class:`~enum.Enum` that contains the valid types of orders.
    """
    LIMIT = 'Limit'
    MARKET = 'Market'
    MARKETABLE_LIMIT = 'Marketable Limit'
    STOP = 'Stop'
    STOP_LIMIT = 'Stop Limit'
    NOTIONAL_MARKET = 'Notional Market'

class OrderTimeInForce(str, Enum):
    """
    This is an :class:`~enum.Enum` that contains the valid TIFs for orders.
    """
    DAY = 'Day'
    GTC = 'GTC'
    GTD = 'GTD'
    EXT = 'Ext'
    GTC_EXT = 'GTC Ext'
    IOC = 'IOC'

class OrderStatus(str, Enum):
    """
    This is an :class:`~enum.Enum` that contains different order statuses.
    A typical (successful) order follows a progression:

    RECEIVED -> LIVE -> FILLED
    """
    RECEIVED = 'Received'
    CANCELLED = 'Cancelled'
    FILLED = 'Filled'
    EXPIRED = 'Expired'
    LIVE = 'Live'
    REJECTED = 'Rejected'
    CONTINGENT = 'Contingent'

class OrderConditionPriceComponent(JsonDataclass):
    """
    Dataclass that represents a price component of an order condition.
    """
    symbol: str
    instrument_type: InstrumentType
    quantity: Decimal
    quantity_direction: str

class OrderCondition(JsonDataclass):
    """
    Dataclass that represents an order condition for an order rule.
    """
    id: str
    action: str
    symbol: str
    instrument_type: InstrumentType
    indicator: str
    comparator: str
    threshold: Decimal
    is_threshold_based_on_notional: bool
    triggered_at: datetime
    triggered_value: Decimal
    price_components: list[OrderConditionPriceComponent]

class OrderRule(JsonDataclass):
    """
    Dataclass that represents an order rule for a complex order.
    """
    route_after: datetime
    routed_at: datetime
    cancel_at: datetime
    cancelled_at: datetime
    order_conditions: list[OrderCondition]

class OrderAction(str, Enum):
    """
    This is an :class:`~enum.Enum` that contains the valid order actions.
    """
    BUY_TO_OPEN = 'Buy to Open'
    BUY_TO_CLOSE = 'Buy to Close'
    SELL_TO_OPEN = 'Sell to Open'
    SELL_TO_CLOSE = 'Sell to Close'
    #: for futures only
    BUY = 'Buy'
    #: for futures only
    SELL = 'Sell'

class FillInfo(JsonDataclass):
    """
    Dataclass that contains information about an order fill.
    """
    ext_group_fill_id: str
    ext_exec_id: str
    fill_id: str
    quantity: Decimal
    fill_price: Decimal
    filled_at: datetime
    destination_venue: str

class Leg(JsonDataclass):
    """
    Dataclass that represents an order leg.

    Classes that inherit from :class:`TradeableJsonDataclass` can
    call :meth:`build_leg` to build a leg from the dataclass.
    """
    instrument_type: InstrumentType
    symbol: str
    action: OrderAction
    quantity: Decimal
    remaining_quantity: Optional[Decimal] = None
    fills: Optional[list[FillInfo]] = None

class PlacedOrder(JsonDataclass):
    """
    Dataclass containing information about an existing order, whether it's
    been filled or not.
    """
    account_number: str
    time_in_force: OrderTimeInForce
    order_type: OrderType
    size: str
    underlying_symbol: str
    underlying_instrument_type: InstrumentType
    status: OrderStatus
    cancellable: bool
    editable: bool
    edited: bool
    updated_at: datetime
    legs: list[Leg]
    id: Optional[str] = None
    price: Optional[Decimal] = None
    price_effect: Optional[PriceEffect] = None
    gtc_date: Optional[date] = None
    value: Optional[Decimal] = None
    value_effect: Optional[PriceEffect] = None
    stop_trigger: Optional[str] = None
    contingent_status: Optional[str] = None
    confirmation_status: Optional[str] = None
    cancelled_at: Optional[datetime] = None
    cancel_user_id: Optional[str] = None
    cancel_username: Optional[str] = None
    replacing_order_id: Optional[str] = None
    replaces_order_id: Optional[str] = None
    in_flight_at: Optional[datetime] = None
    live_at: Optional[datetime] = None
    received_at: Optional[datetime] = None
    reject_reason: Optional[str] = None
    user_id: Optional[str] = None
    username: Optional[str] = None
    terminal_at: Optional[datetime] = None
    complex_order_id: Optional[str] = None
    complex_order_tag: Optional[str] = None
    preflight_id: Optional[str] = None
    order_rule: Optional[OrderRule] = None

class OrderStatus(str, Enum):
    """
    This is an :class:`~enum.Enum` that contains different order statuses.
    A typical (successful) order follows a progression:

    RECEIVED -> LIVE -> FILLED
    """
    RECEIVED = 'Received'
    CANCELLED = 'Cancelled'
    FILLED = 'Filled'
    EXPIRED = 'Expired'
    LIVE = 'Live'
    REJECTED = 'Rejected'
    CONTINGENT = 'Contingent'

class NewOrder(JsonDataclass):
    """
    Dataclass containing information about a new order. Also used for
    modifying existing orders.
    """
    time_in_force: OrderTimeInForce
    order_type: OrderType
    source: str = f'ttapi'
    legs: list[Leg]
    gtc_date: Optional[date] = None
    stop_trigger: Optional[Decimal] = None
    price: Optional[Decimal] = None  # optional for market orders
    price_effect: Optional[PriceEffect] = None
    value: Optional[Decimal] = None
    value_effect: Optional[PriceEffect] = None
    partition_key: Optional[str] = None
    preflight_id: Optional[str] = None
    rules: Optional[OrderRule] = None

class BuyingPowerEffect(JsonDataclass):
    """
    Dataclass containing information about the effect of a trade on buying
    power.
    """
    change_in_margin_requirement: Decimal
    change_in_margin_requirement_effect: PriceEffect
    change_in_buying_power: Decimal
    change_in_buying_power_effect: PriceEffect
    current_buying_power: Decimal
    current_buying_power_effect: PriceEffect
    new_buying_power: Decimal
    new_buying_power_effect: PriceEffect
    isolated_order_margin_requirement: Decimal
    isolated_order_margin_requirement_effect: PriceEffect
    is_spread: bool
    impact: Decimal
    effect: PriceEffect

class FeeCalculation(JsonDataclass):
    """
    Dataclass containing information about the fees associated with a trade.
    """
    regulatory_fees: Decimal
    regulatory_fees_effect: PriceEffect
    clearing_fees: Decimal
    clearing_fees_effect: PriceEffect
    commission: Decimal
    commission_effect: PriceEffect
    proprietary_index_option_fees: Decimal
    proprietary_index_option_fees_effect: PriceEffect
    total_fees: Decimal
    total_fees_effect: PriceEffect

class ComplexOrder(JsonDataclass):
    """
    Dataclass containing information about a complex order.
    """
    id: str
    account_number: str
    type: str
    terminal_at: str
    ratio_price_threshold: Decimal
    ratio_price_comparator: str
    ratio_price_is_threshold_based_on_notional: bool
    related_orders: list[dict[str, str]]
    orders: list[PlacedOrder]
    trigger_order: PlacedOrder

class Message(JsonDataclass):
    """
    Dataclass that represents a message from the Tastytrade API, usually
    a warning or an error.
    """
    code: str
    message: str
    preflight_id: Optional[str] = None

    def __str__(self):
        return f'{self.code}: {self.message}'

class PlacedOrderResponse(JsonDataclass):
    """
    Dataclass grouping together information about a placed order.
    """
    buying_power_effect: BuyingPowerEffect
    fee_calculation: FeeCalculation
    order: Optional[PlacedOrder] = None
    complex_order: Optional[ComplexOrder] = None
    warnings: Optional[list[Message]] = None
    errors: Optional[list[Message]] = None


class TradeableJsonDataclass(JsonDataclass):
    """
    Dataclass that represents a tradeable instrument.

    Classes that inherit from this class can call :meth:`build_leg` to build a
    leg from the dataclass.
    """
    instrument_type: InstrumentType
    symbol: str

    def build_leg(self, quantity: Decimal, action: OrderAction) -> Leg:
        """
        Builds an order Leg from the dataclass.

        :param quantity: the quantity of the symbol to trade
        :param action: :class:`OrderAction` to perform, e.g. BUY_TO_OPEN

        :return: a Leg object
        """
        return Leg(
            instrument_type=self.instrument_type,
            symbol=self.symbol,
            quantity=quantity,
            action=action
        )
    

class TickSize(JsonDataclass):
    """
    Dataclass representing the tick size for an instrument.
    """
    value: Decimal
    threshold: Optional[Decimal] = None
    symbol: Optional[str] = None

class TotalFees(JsonDataclass):
    """
    Dataclass representing the total fees amount
    """
    total_fees: Optional[Decimal] = None
    total_fees_effect: Optional[Decimal] = None

    @validator('total_fees_effect', pre=True)
    def nonestr_to_none(cls, v):
        if v == 'None':
            v = None
        return v

class SymbolData(JsonDataclass):
    """
    Dataclass holding search results for an individual item.
    """
    symbol: str
    description: str

class OptionType(str, Enum):
    """
    This is an :class:`~enum.Enum` that contains the valid types of options and
    their abbreviations in the API.
    """
    CALL = 'C'
    PUT = 'P'

class Deliverable(JsonDataclass):
    """
    Dataclass representing the deliverable for an option.
    """
    id: int
    root_symbol: str
    deliverable_type: str
    description: str
    amount: Decimal
    symbol: str
    instrument_type: InstrumentType
    percent: str

class Strike(JsonDataclass):
    """
    Dataclass representing a specific strike in an options chain, containing the
    symbols for the call and put options.
    """
    strike_price: Decimal
    call: str
    put: str

class NestedOptionChainExpiration(JsonDataclass):
    """
    Dataclass representing an expiration in a nested options chain.
    """
    expiration_type: str
    expiration_date: date
    days_to_expiration: int
    settlement_type: str
    strikes: list[Strike]

class FutureMonthCode(str, Enum):
    """
    This is an :class:`~enum.Enum` that contains the valid month codes for futures.

    This is really just here for reference, as the API barely uses these codes.
    """
    JAN = 'F'
    FEB = 'G'
    MAR = 'H'
    APR = 'J'
    MAY = 'K'
    JUN = 'M'
    JUL = 'N'
    AUG = 'Q'
    SEP = 'U'
    OCT = 'V'
    NOV = 'X'
    DEC = 'Z'

class Roll(JsonDataclass):
    """
    Dataclass representing a roll for a future.
    """
    name: str
    active_count: int
    cash_settled: bool
    business_days_offset: int
    first_notice: bool

class FutureEtfEquivalent(JsonDataclass):
    """
    Dataclass that represents the ETF equivalent for a future (aka, the number
    of shares of the ETF that are equivalent to one future, leverage-wise).
    """
    symbol: str
    share_quantity: int

class NestedFutureOptionFuture(JsonDataclass):
    """
    Dataclass representing an underlying future in a nested future options chain.
    """
    root_symbol: str
    days_to_expiration: int
    expiration_date: date
    expires_at: datetime
    next_active_month: bool
    symbol: str
    active_month: bool
    stops_trading_at: datetime
    maturity_date: Optional[date] = None

class NestedFutureOptionChainExpiration(JsonDataclass):
    """
    Dataclass representing an expiration in a nested future options chain.
    """
    root_symbol: str
    notional_value: Decimal
    underlying_symbol: str
    strike_factor: Decimal
    days_to_expiration: int
    option_root_symbol: str
    expiration_date: date
    expires_at: datetime
    asset: str
    expiration_type: str
    display_factor: Decimal
    option_contract_symbol: str
    stops_trading_at: datetime
    settlement_type: str
    strikes: list[Strike]
    tick_sizes: list[TickSize]


class NestedFutureOptionSubchain(JsonDataclass):
    """
    Dataclass that represents a Tastytrade nested future option chain for a
    specific futures underlying symbol.
    """
    underlying_symbol: str
    root_symbol: str
    exercise_style: str
    expirations: list[NestedFutureOptionChainExpiration]


class QuantityDecimalPrecision(JsonDataclass):
    """
    Dataclass representing the decimal precision (number of places) for an instrument.
    """
    instrument_type: InstrumentType
    value: int
    minimum_increment_precision: int
    symbol: Optional[str] = None


class DividendInfo(JsonDataclass):
    """
    Dataclass representing dividend information for a given symbol.
    """
    occurred_date: date
    amount: Decimal


class EarningsInfo(JsonDataclass):
    """
    Dataclass representing earnings information for a given symbol.
    """
    occurred_date: date
    eps: Decimal


class Liquidity(JsonDataclass):
    """
    Dataclass representing liquidity information for a given symbol.
    """
    sum: Decimal
    count: int
    started_at: datetime
    updated_at: Optional[datetime] = None


class OptionExpirationImpliedVolatility(JsonDataclass):
    """
    Dataclass containing implied volatility information for a given symbol
    and expiration date.
    """
    expiration_date: date
    settlement_type: str
    option_chain_type: str
    implied_volatility: Optional[Decimal] = None


class MarketMetricInfo(JsonDataclass):
    """
    Dataclass representing market metrics for a given symbol.

    Contains lots of useful information, like IV rank, IV percentile and beta.
    """
    symbol: str
    implied_volatility_index: Decimal
    implied_volatility_index_5_day_change: Decimal
    implied_volatility_index_rank: Decimal
    tos_implied_volatility_index_rank: Decimal
    tw_implied_volatility_index_rank: Decimal
    tos_implied_volatility_index_rank_updated_at: datetime
    implied_volatility_index_rank_source: str
    implied_volatility_percentile: Decimal
    implied_volatility_updated_at: datetime
    liquidity_value: Decimal
    liquidity_rank: Decimal
    liquidity_rating: int
    created_at: Optional[datetime] = None
    updated_at: datetime
    option_expiration_implied_volatilities: list[OptionExpirationImpliedVolatility]
    liquidity_running_state: Liquidity
    beta: Decimal
    beta_updated_at: datetime
    corr_spy_3month: Decimal
    dividend_rate_per_share: Decimal
    dividend_yield: Decimal
    listed_market: str
    lendability: str
    borrow_rate: Decimal
    market_cap: Decimal
    implied_volatility_30_day: Decimal
    historical_volatility_30_day: Decimal
    historical_volatility_60_day: Decimal
    historical_volatility_90_day: Decimal
    iv_hv_30_day_difference: Decimal
    price_earnings_ratio: Decimal
    earnings_per_share: Decimal
    dividend_ex_date: Optional[date] = None
    dividend_next_date: Optional[date] = None
    dividend_pay_date: Optional[date] = None
    dividend_updated_at: Optional[datetime] = None


class SubscriptionType(str, Enum):
    """
    This is an :class:`~enum.Enum` that contains the subscription types for the alert streamer.
    """
    ACCOUNT = 'account-subscribe'  # 'account-subscribe' may be deprecated in the future
    HEARTBEAT = 'heartbeat'
    PUBLIC_WATCHLISTS = 'public-watchlists-subscribe'
    QUOTE_ALERTS = 'quote-alerts-subscribe'
    USER_MESSAGE = 'user-message-subscribe'


class QuoteAlert(JsonDataclass):
    """
    Dataclass that contains information about a quote alert
    """
    user_external_id: str
    symbol: str
    alert_external_id: str
    expires_at: int
    completed_at: datetime
    created_at: datetime
    triggered_at: datetime
    field: str
    operator: str
    threshold: str
    threshold_numeric: Decimal
    dx_symbol: str


class UnderlyingYearGainSummary(JsonDataclass):
    """
    Dataclass that contains information about the yearly gainYloss for an underlying
    """
    year: int
    account_number: str
    symbol: str
    instrument_type: InstrumentType
    fees: Decimal
    fees_effect: PriceEffect
    commissions: Decimal
    commissions_effect: PriceEffect
    yearly_realized_gain: Decimal
    yearly_realized_gain_effect: PriceEffect
    realized_lot_gain: Decimal
    realized_lot_gain_effect: PriceEffect


class InstrumentType(str, Enum):
    """
    This is an :class:`~enum.Enum` that contains the valid types of instruments
    and their representation in the API.
    """
    BOND = 'Bond'
    CRYPTOCURRENCY = 'Cryptocurrency'
    CURRENCY_PAIR = 'Currency Pair'
    EQUITY = 'Equity'
    EQUITY_OFFERING = 'Equity Offering'
    EQUITY_OPTION = 'Equity Option'
    FUTURE = 'Future'
    FUTURE_OPTION = 'Future Option'
    INDEX = 'Index'
    UNKNOWN = 'Unknown'
    WARRANT = 'Warrant'


class OrderAction(str, Enum):
    """
    This is an :class:`~enum.Enum` that contains the valid order actions.
    """
    BUY_TO_OPEN = 'Buy to Open'
    BUY_TO_CLOSE = 'Buy to Close'
    SELL_TO_OPEN = 'Sell to Open'
    SELL_TO_CLOSE = 'Sell to Close'
    #: for futures only
    BUY = 'Buy'
    #: for futures only
    SELL = 'Sell'


class OrderStatus(str, Enum):
    """
    This is an :class:`~enum.Enum` that contains different order statuses.
    A typical (successful) order follows a progression:

    RECEIVED -> LIVE -> FILLED
    """
    RECEIVED = 'Received'
    CANCELLED = 'Cancelled'
    FILLED = 'Filled'
    EXPIRED = 'Expired'
    LIVE = 'Live'
    REJECTED = 'Rejected'
    CONTINGENT = 'Contingent'
    ROUTED = 'Routed'
    IN_FLIGHT = 'In Flight'
    CANCEL_REQUESTED = 'Cancel Requested'
    REPLACE_REQUESTED = 'Replace Requested'
    REMOVED = 'Removed'
    PARTIALLY_REMOVED = 'Partially Removed'


class OrderTimeInForce(str, Enum):
    """
    This is an :class:`~enum.Enum` that contains the valid TIFs for orders.
    """
    DAY = 'Day'
    GTC = 'GTC'
    GTD = 'GTD'
    EXT = 'Ext'
    GTC_EXT = 'GTC Ext'
    IOC = 'IOC'


class OrderType(str, Enum):
    """
    This is an :class:`~enum.Enum` that contains the valid types of orders.
    """
    LIMIT = 'Limit'
    MARKET = 'Market'
    MARKETABLE_LIMIT = 'Marketable Limit'
    STOP = 'Stop'
    STOP_LIMIT = 'Stop Limit'
    NOTIONAL_MARKET = 'Notional Market'


class PriceEffect(str, Enum):
    """
    This is an :class:`~enum.Enum` that shows the sign of a price effect, since
    Tastytrade is apparently against negative numbers.
    """
    CREDIT = 'Credit'
    DEBIT = 'Debit'
    NONE = 'None'


class FillInfo(JsonDataclass):
    """
    Dataclass that contains information about an order fill.
    """
    ext_group_fill_id: str
    ext_exec_id: str
    fill_id: str
    quantity: Decimal
    fill_price: Decimal
    filled_at: datetime
    destination_venue: str


class Leg(JsonDataclass):
    """
    Dataclass that represents an order leg.

    Classes that inherit from :class:`TradeableJsonDataclass` can
    call :meth:`build_leg` to build a leg from the dataclass.
    """
    instrument_type: InstrumentType
    symbol: str
    action: OrderAction
    quantity: Decimal
    remaining_quantity: Optional[Decimal] = None
    fills: Optional[list[FillInfo]] = None


class TradeableJsonDataclass(JsonDataclass):
    """
    Dataclass that represents a tradeable instrument.

    Classes that inherit from this class can call :meth:`build_leg` to build a
    leg from the dataclass.
    """
    instrument_type: InstrumentType
    symbol: str

    def build_leg(self, quantity: Decimal, action: OrderAction) -> Leg:
        """
        Builds an order :class:`Leg` from the dataclass.

        :param quantity: the quantity of the symbol to trade
        :param action: :class:`OrderAction` to perform, e.g. BUY_TO_OPEN

        :return: a :class:`Leg` object
        """
        return Leg(
            instrument_type=self.instrument_type,
            symbol=self.symbol,
            quantity=quantity,
            action=action
        )


class Message(JsonDataclass):
    """
    Dataclass that represents a message from the Tastytrade API, usually
    a warning or an error.
    """
    code: str
    message: str
    preflight_id: Optional[str] = None

    def __str__(self):
        return f'{self.code}: {self.message}'


class OrderConditionPriceComponent(JsonDataclass):
    """
    Dataclass that represents a price component of an order condition.
    """
    symbol: str
    instrument_type: InstrumentType
    quantity: Decimal
    quantity_direction: str


class OrderCondition(JsonDataclass):
    """
    Dataclass that represents an order condition for an order rule.
    """
    id: str
    action: str
    symbol: str
    instrument_type: InstrumentType
    indicator: str
    comparator: str
    threshold: Decimal
    is_threshold_based_on_notional: bool
    triggered_at: datetime
    triggered_value: Decimal
    price_components: list[OrderConditionPriceComponent]


class OrderRule(JsonDataclass):
    """
    Dataclass that represents an order rule for a complex order.
    """
    route_after: datetime
    routed_at: datetime
    cancel_at: datetime
    cancelled_at: datetime
    order_conditions: list[OrderCondition]


class NewOrder(JsonDataclass):
    """
    Dataclass containing information about a new order. Also used for
    modifying existing orders.
    """
    time_in_force: OrderTimeInForce
    order_type: OrderType
    source: str = f'ttapi'
    legs: list[Leg]
    gtc_date: Optional[date] = None
    stop_trigger: Optional[Decimal] = None
    price: Optional[Decimal] = None  # optional for market orders
    price_effect: Optional[PriceEffect] = None
    value: Optional[Decimal] = None
    value_effect: Optional[PriceEffect] = None
    partition_key: Optional[str] = None
    preflight_id: Optional[str] = None
    rules: Optional[OrderRule] = None


class PlacedOrder(JsonDataclass):
    """
    Dataclass containing information about an existing order, whether it's
    been filled or not.
    """
    account_number: str
    time_in_force: OrderTimeInForce
    order_type: OrderType
    size: str
    underlying_symbol: str
    underlying_instrument_type: InstrumentType
    status: OrderStatus
    cancellable: bool
    editable: bool
    edited: bool
    updated_at: datetime
    legs: list[Leg]
    id: Optional[str] = None
    price: Optional[Decimal] = None
    price_effect: Optional[PriceEffect] = None
    gtc_date: Optional[date] = None
    value: Optional[Decimal] = None
    value_effect: Optional[PriceEffect] = None
    stop_trigger: Optional[str] = None
    contingent_status: Optional[str] = None
    confirmation_status: Optional[str] = None
    cancelled_at: Optional[datetime] = None
    cancel_user_id: Optional[str] = None
    cancel_username: Optional[str] = None
    replacing_order_id: Optional[str] = None
    replaces_order_id: Optional[str] = None
    in_flight_at: Optional[datetime] = None
    live_at: Optional[datetime] = None
    received_at: Optional[datetime] = None
    reject_reason: Optional[str] = None
    user_id: Optional[str] = None
    username: Optional[str] = None
    terminal_at: Optional[datetime] = None
    complex_order_id: Optional[str] = None
    complex_order_tag: Optional[str] = None
    preflight_id: Optional[str] = None
    order_rule: Optional[OrderRule] = None


class ComplexOrder(JsonDataclass):
    """
    Dataclass containing information about a complex order.
    """
    id: str
    account_number: str
    type: str
    terminal_at: str
    ratio_price_threshold: Decimal
    ratio_price_comparator: str
    ratio_price_is_threshold_based_on_notional: bool
    related_orders: list[dict[str, str]]
    orders: list[PlacedOrder]
    trigger_order: PlacedOrder


class BuyingPowerEffect(JsonDataclass):
    """
    Dataclass containing information about the effect of a trade on buying
    power.
    """
    change_in_margin_requirement: Decimal
    change_in_margin_requirement_effect: PriceEffect
    change_in_buying_power: Decimal
    change_in_buying_power_effect: PriceEffect
    current_buying_power: Decimal
    current_buying_power_effect: PriceEffect
    new_buying_power: Decimal
    new_buying_power_effect: PriceEffect
    isolated_order_margin_requirement: Decimal
    isolated_order_margin_requirement_effect: PriceEffect
    is_spread: bool
    impact: Decimal
    effect: PriceEffect


class FeeCalculation(JsonDataclass):
    """
    Dataclass containing information about the fees associated with a trade.
    """
    regulatory_fees: Decimal
    regulatory_fees_effect: PriceEffect
    clearing_fees: Decimal
    clearing_fees_effect: PriceEffect
    commission: Decimal
    commission_effect: PriceEffect
    proprietary_index_option_fees: Decimal
    proprietary_index_option_fees_effect: PriceEffect
    total_fees: Decimal
    total_fees_effect: PriceEffect


class PlacedOrderResponse(JsonDataclass):
    """
    Dataclass grouping together information about a placed order.
    """
    buying_power_effect: BuyingPowerEffect
    fee_calculation: FeeCalculation
    order: Optional[PlacedOrder] = None
    complex_order: Optional[ComplexOrder] = None
    warnings: Optional[list[Message]] = None
    errors: Optional[list[Message]] = None


class OrderChainEntry(JsonDataclass):
    """
    Dataclass containing information about a single order in an order chain.
    """
    symbol: str
    instrument_type: InstrumentType
    quantity: str
    quantity_type: str
    quantity_numeric: Decimal


class OrderChainLeg(JsonDataclass):
    """
    Dataclass containing information about a single leg in an order from an order chain.
    """
    symbol: str
    instrument_type: InstrumentType
    action: OrderAction
    fill_quantity: Decimal
    order_quantity: Decimal


class OrderChainNode(JsonDataclass):
    """
    Dataclass containing information about a single node in an order chain.
    """
    node_type: str
    id: str
    description: str
    occurred_at: Optional[datetime] = None
    total_fees: Optional[Decimal] = None
    total_fees_effect: Optional[PriceEffect] = None
    total_fill_cost: Optional[Decimal] = None
    total_fill_cost_effect: Optional[PriceEffect] = None
    gcd_quantity: Optional[Decimal] = None
    fill_cost_per_quantity: Optional[Decimal] = None
    fill_cost_per_quantity_effect: Optional[PriceEffect] = None
    order_fill_count: Optional[int] = None
    roll: Optional[bool] = None
    legs: Optional[list[OrderChainLeg]] = None
    entries: Optional[list[OrderChainEntry]] = None


class ComputedData(JsonDataclass):
    """
    Dataclass containing computed data about an order chain.
    """
    open: bool
    updated_at: datetime
    total_fees: Decimal
    total_fees_effect: PriceEffect
    total_commissions: Decimal
    total_commissions_effect: PriceEffect
    realized_gain: Decimal
    realized_gain_effect: PriceEffect
    realized_gain_with_fees: Decimal
    realized_gain_with_fees_effect: PriceEffect
    winner_realized_and_closed: bool
    winner_realized: bool
    winner_realized_with_fees: bool
    roll_count: int
    opened_at: datetime
    last_occurred_at: datetime
    started_at_days_to_expiration: int
    duration: int
    total_opening_cost: Decimal
    total_opening_cost_effect: PriceEffect
    total_closing_cost: Decimal
    total_closing_cost_effect: PriceEffect
    total_cost: Decimal
    total_cost_effect: PriceEffect
    gcd_open_quantity: Decimal
    fees_missing: bool
    open_entries: list[OrderChainEntry]
    total_cost_per_unit: Optional[Decimal] = None
    total_cost_per_unit_effect: Optional[PriceEffect] = None


class OrderChain(JsonDataclass):
    """
    Dataclass containing information about an order chain: a group of orders for a
    specific underlying, such as total P/L, rolls, current P/L in a symbol, etc.
    """
    id: int
    updated_at: datetime
    created_at: datetime
    account_number: str
    description: str
    underlying_symbol: str
    computed_data: ComputedData
    lite_nodes_sizes: int
    lite_nodes: list[OrderChainNode]

