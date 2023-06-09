from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Optional
from ttapi.exceptions import TastyTradeException
from ttapi.models import JsonDataclass
from ttapi.session import Session
from ttapi.models import (TradingStatus, AccountBalance, AccountBalanceSnapshot, 
                          InstrumentType, Position, Transaction, NetLiquidation,
                          PositionLimit, MarginRequirement, MarginReport,
                          PlacedOrder, OrderStatus, NewOrder, PlacedOrderResponse, 
                          TotalFees)

class Account(JsonDataclass):
    """
    Dataclass that represents a account object
    """
    account_number: str
    opened_at: datetime
    nickname: str
    account_type_name: str
    is_closed: bool
    day_trader_status: str
    is_firm_error: bool
    is_firm_proprietary: bool
    is_futures_approved: bool
    is_test_drive: bool
    margin_or_cash: str
    is_foreign: bool
    created_at: datetime
    external_id: Optional[str] = None
    closed_at: Optional[str] = None
    funding_date: Optional[date] = None
    investment_objective: Optional[str] = None
    liquidity_needs: Optional[str] = None
    risk_tolerance: Optional[str] = None
    investment_time_horizon: Optional[str] = None
    futures_account_purpose: Optional[str] = None
    external_fdid: Optional[str] = None
    suitable_options_level: Optional[str] = None
    submitting_user_id: Optional[str] = None

    @classmethod
    def get_accounts(cls, session: Session) -> list['Account']:
        """
        Gets all trading accounts
        :param adapter: the object that performs the requests
        :return: a lists of `Account` objects
        """

        response = session.request('GET', '/customers/me/accounts')

        accounts = []
        for item in response.data['data']['items']:
            account = item['account']
            accounts.append(cls(**account))
    
        return accounts
    
    @classmethod
    def get_account(cls, session: Session, account_number: str) -> 'Account':
        """
        Get a account object for a given ID
        : the account ID to get
        :param adapter: the object that performs the requests

        :return: a Account object
        """
        response = session.request('GET', f'/customers/me/accounts/{account_number}')
        account = response.data['data']
        return cls(**account)
    

    def get_trading_status(self, session: Session) -> TradingStatus:
        """
        Get the tranding status of the current account
        :param adapter: the object that performs the requests
        :return: a TradingStatus object
        """
        response = session.request('GET', f'/accounts/{self.account_number}/trading-status')
        status = response.data['data']
        return TradingStatus(**status)
    

    def get_balances(self, session: Session) -> AccountBalance:
        """
        Get the current balances of the current account.

        :param session: the session to use for the request.
        :return: a AccountBalance object
        """
        response = session.request('GET', f'/accounts/{self.account_number}/balances')
        balance = response.data['data']
        return AccountBalance(**balance)
    
    def get_balance_snapshots(self, 
                              session: Session,
                              snapshot_date: Optional[date] = None,
                              time_of_day: Optional[str] = None) -> AccountBalanceSnapshot:
        """
        Returns two balance snapshots:
            1) the date/time snapshot specified
            2) the most recent snapshot

        :param session: the session to use for the request.
        :param snapshot_date: the date of the snapshot to get.
        :param time_of_day: the time of day of the snapshot to get, either 'EOD' or 'BOD'.

        :return: a list of two 'AccountBalanceSnapshot' objects.

        """
        payload: dict[str, Any] = {
            'snapshot-date': snapshot_date,
            'time-of-day': time_of_day    
        }

        response = session.request('GET', f'/accounts/{self.account_number}/balance-snapshots', params=payload)
        return [AccountBalanceSnapshot(**item) for item in response.data['data']['items']]
    
    def get_positions(
        self,
        session: Session,
        underlying_symbols: Optional[list[str]] = None,
        symbol: Optional[str] = None,
        instrument_type: Optional[InstrumentType] = None,
        include_closed: bool = False,
        underlying_product_code: Optional[str] = None,
        partition_keys: Optional[list[str]] = None,
        net_positions: bool = False,
        include_marks: bool = False
    ) -> list[Position]:
        """
        Get the current positions of the account.

        :param session: the session to use for the request.
        :param underlying_symbols: an array of underlying symbols for positions.
        :param symbol: a single symbol.
        :param instrument_type: the type of instrument.
        :param include_closed: if closed positions should be included in the query.
        :param underlying_product_code: the underlying future's product code.
        :param partition_keys: account partition keys.
        :param net_positions: returns net positions grouped by instrument type and symbol.
        :param include_marks: include current quote mark (note: can decrease performance).

        :return: a list of 'Position' objects in JSON format.
        """
        payload: dict[str, Any] = {
            'underlying-symbol[]': underlying_symbols,
            'symbol': symbol,
            'instrument-type': instrument_type,
            'include-closed-positions': include_closed,
            'underlying-product-code': underlying_product_code,
            'partition-keys[]': partition_keys,
            'net-positions': net_positions,
            'include-marks': include_marks
        }
    
        response = session.request('GET', f'/accounts/{self.account_number}/positions', params=payload)
        return [Position(**item ) for item in response.data['data']['items']]
    
    def get_transactions(
            self,
            session: Session,
            per_page: int = 100,
            page_offset: Optional[int] = None,
            sort: str = 'Desc',
            type: Optional[str] = None,
            types: Optional[list[str]] = None,
            sub_types: Optional[list[str]] = None,
            start_date: Optional[date] = None,
            end_date: date = date.today(),
            instrument_type: Optional[InstrumentType] = None,
            symbol: Optional[str] = None,
            underlying_symbol: Optional[str] = None,
            action: Optional[str] = None,
            partition_key: Optional[str] = None,
            futures_symbol: Optional[str] = None,
            start_at: Optional[datetime] = None,
            end_at: Optional[datetime] = None
        ) -> list[Transaction]:
            """
            Get transaction history of the account.

            :param session: the session to use for the request.
            :param per_page: the number of results to return per page.
            :param page_offset: provide a specific page to get; if not provided, get all pages
            :param sort: the order to sort results in, either 'Desc' or 'Asc'.
            :param type: the type of transaction.
            :param types: a list of transaction types to filter by.
            :param sub_types: an array of transaction subtypes to filter by.
            :param start_date: the start date of transactions to query.
            :param end_date: the end date of transactions to query.
            :param instrument_type: the type of instrument.
            :param symbol: a single symbol.
            :param underlying_symbol: the underlying symbol.
            :param action:
                the action of the transaction: 'Sell to Open', 'Sell to Close', 'Buy to Open',
                'Buy to Close', 'Sell' or 'Buy'.
            :param partition_key: account partition key.
            :param futures_symbol: the full TW Future Symbol, e.g. /ESZ9, /NGZ19.
            :param start_at: datetime start range for filtering transactions in full date-time.
            :param end_at: datetime end range for filtering transactions in full date-time.

            :return: a list of Tastytrade 'Transaction' objects
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
                'sort': sort,
                'type': type,
                'types[]': types,
                'sub-type[]': sub_types,
                'start-date': start_date,
                'end-date': end_date,
                'instrument-type': instrument_type,
                'symbol': symbol,
                'underlying-symbol': underlying_symbol,
                'action': action,
                'partition-key': partition_key,
                'futures-symbol': futures_symbol,
                'start-at': start_at,
                'end-at': end_at
            }
            
            payload = {k: v for k,v in payload.items() if v is not None}
            pages = []
            while True:
                response = session.request('GET', f'/accounts/{self.account_number}/transactions', params=payload)
                pages.extend(response.data['data']['items'])
                
                pagination = response.data['pagination']
            
                if pagination['page-offset'] >= pagination['total-pages'] - 1: # finished
                    break
                if not paginate:
                    break
                
                payload['page-offset'] += 1  # type: ignore

            return [Transaction(**item) for item in pages]

    def get_transaction(self, session: Session, id: int) -> Transaction:
        """
        Get a single transaction by ID.

        :param session: the session to use for the request.
        :param id: the ID of the transaction to fetch.

        :return: a Transaction object.
        """
        response = session.request('GET', f'/accounts/{self.account_number}/transactions/{id}')
        return Transaction(**response.data['data'])
    
    def get_total_fees(self, session: Session, date: date = date.today()) -> dict[str, Any]:
        """
        Get the total fees for a given date.

        :param session: the session to use for the request.
        :param date: the date to get fees for.

        :return: a TotalFees object.
        """
        payload: dict[str, Any] = {'date': date}
        response = session.request('GET', f'/accounts/{self.account_number}/transactions/total-fees', params=payload)
        return TotalFees(**response.data['data'])
    
    def get_net_liquidating_value_history(
        self,
        session: Session,
        time_back: Optional[str] = None,
        start_time: Optional[datetime] = None
        ) -> list[NetLiquidation]:
        """
        Returns a list of account net liquidating value snapshots over the specified time period.

        :param session: the session to use for the request.
        :param time_back:
            the time period to get net liquidating value snapshots for. This param is required
            if start_time is not given. Possible values are: '1d', '1m', '3m', '6m', '1y', 'all'.
        :param start_time:
            the start point for the query. This param is required is time-back is not given.
            If given, will take precedence over time-back.

        :return: a list of NetLiquidation objects
        """
    
        payload: dict[str, Any] = {}
        if start_time:
            # format to Tastytrade DateTime format
            start_time = str(start_time).replace(' ', 'T').split('.')[0] + 'Z'
            payload = {'start-time': start_time}
        elif not time_back:
            raise TastyTradeException('Either time_back or start_time must be specified.')
        else:
            payload = {'time-back': time_back}

        response = session.request('GET', f'/accounts/{self.account_number}/net-liq/history', params=payload)
        return [NetLiquidation(**item ) for item in response.data['data']['items']]


    def get_position_limit(self, session: Session) -> PositionLimit:
        """
        Get the maximum order size information for the account.

        :param session: the session to use for the request.

        :return: a PositionLimit object.
        """
        response = session.request('GET', f'/accounts/{self.account_number}/position-limit')
        return PositionLimit(**response.data['data'])

    def get_margin_requirements(self, session: Session) -> MarginReport:
        """
        Get the margin report for the account, with total margin requirements as well
        as a breakdown per symbol/instrument.

        :param session: the session to use for the request.

        :return: a MarginReport object.
        """
        response = session.request('GET', f'/margin/accounts/{self.account_number}/requirements')
        return MarginReport(**response.data['data'])


    def get_effective_margin_requirements(self, session: Session, symbol: str) -> MarginRequirement:
        """
        Get the effective margin requirements for a given symbol.

        :param session: the session to use for the request.
        :param symbol: the symbol to get margin requirements for.

        :return: a :class:`MarginRequirement` object.
        """

        if symbol:
            symbol = symbol.replace('/', '%2F')
        
        response = session.request('GET', f'/accounts/{self.account_number}/margin-requirements/{symbol}/effective')
        return MarginRequirement(**response.data['data'])
    

    def get_live_orders(self, session: Session) -> list[PlacedOrder]:
        """
        Get all live orders for the account.

        :param session: the session to use for the request.

        :return: a list of Order objects.
        """

        response = session.request('GET', f'/accounts/{self.account_number}/orders/live')
        return [PlacedOrder(**item ) for item in response.data['data']['items']]

    def get_order(self, session: Session, order_id: str) -> PlacedOrder:
        """
        Gets an order with the given ID.

        :param session: the session to use for the request.

        :return: an Order object corresponding to the given ID.
        """
        response = session.request('GET', f'/accounts/{self.account_number}/orders/{order_id}')
        return PlacedOrder(**response.data['data'])
    
    def delete_order(self, session: Session, order_id: str) -> None:
        """
        Delete an order by ID.

        :param session: the session to use for the request.
        :param order_id: the ID of the order to delete.
        """
        response = session.request('DELETE', f'/accounts/{self.account_number}/orders/{order_id}')
        return True

    def get_order_history(
        self,
        session: Session,
        per_page: int = 10,
        page_offset: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        underlying_symbol: Optional[str] = None,
        statuses: Optional[list[OrderStatus]] = None,
        futures_symbol: Optional[str] = None,
        underlying_instrument_type: Optional[InstrumentType] = None,
        sort: str = 'Desc',
        start_at: Optional[datetime] = None,
        end_at: Optional[datetime] = None
        ) -> list[PlacedOrder]:
        """
        Get order history of the account.

        :param session: the session to use for the request.
        :param per_page: the number of results to return per page.
        :param page_offset: provide a specific page to get; if not provided, get all pages
        :param start_date: the start date of orders to query.
        :param end_date: the end date of orders to query.
        :param underlying_symbol: underlying symbol to filter by.
        :param statuses: a list of statuses to filter by.
        :param futures_symbol: Tastytrade future symbol for futures and future options.
        :param underlying_instrument_type: the type of instrument to filter by.
        :param sort: the order to sort results in, either 'Desc' or 'Asc'.
        :param start_at: datetime start range for filtering transactions in full date-time.
        :param end_at: datetime end range for filtering transactions in full date-time.

        :return: a list of PlacedOrder objects.
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
            'start-date': start_date,
            'end-date': end_date,
            'underlying-symbol': underlying_symbol,
            'status[]': statuses,
            'futures-symbol': futures_symbol,
            'underlying-instrument-type': underlying_instrument_type,
            'sort': sort,
            'start-at': start_at,
            'end-at': end_at
        }
        payload = {k: v for k,v in payload.items() if v is not None}
        pages = []
        while True:
            response = session.request('GET', f'/accounts/{self.account_number}/orders', params=payload)
            pages.extend(response.data['data']['items'])
            
            pagination = response.data['pagination']
        
            if pagination['page-offset'] >= pagination['total-pages'] - 1: # finished
                break
            if not paginate:
                break
            
            payload['page-offset'] += 1

        return [PlacedOrder(**item) for item in pages]
    
    def place_order(self, session: Session, order: NewOrder, test_order=True) -> PlacedOrderResponse:
        """
        Place the given order.

        :param session: the session to use for the request.
        :param order: the order to place.
        :param dry_run: whether this is a test order or not.

        :return: a PlacedOrderResponse object for the placed order.
        """
        test_order_sufix: str = ''
        if test_order:
            test_order_sufix = '/dry-run'
        
        payload = order.json(exclude_none=True, by_alias=True)
        response = session.request('POST', f'/accounts/{self.account_number}/orders{test_order_sufix}', data=payload)
        return PlacedOrderResponse(**response.data['data'])


    def replace_order(self, session: Session, old_order_id: str, new_order: NewOrder) -> PlacedOrder:
        """
        Replace an order with a new order with different characteristics (but same legs).

        :param session: the session to use for the request.
        :param old_order_id: the ID of the order to replace.
        :param new_order: the new order to replace the old order with.

        :return: a PlacedOrder object for the modified order.
        """
        payload = new_order.json(exclude={'legs'}, exclude_none=True, by_alias=True)
        response = session.request('POST', f'/accounts/{self.account_number}/orders/{old_order_id}', data=payload)
        return PlacedOrderResponse(**response.data['data'])