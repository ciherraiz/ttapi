from unittest.mock import patch, Mock
from ttapi.account import Account
from ttapi.models import (RequestResult, TradingStatus, AccountBalance, 
                          AccountBalanceSnapshot, Position, Transaction,
                          NetLiquidation, PositionLimit, MarginRequirement, 
                          MarginReport, PlacedOrder, TotalFees)
from ttapi.exceptions import AdapterException
import pytest

@pytest.fixture
def session():
    response = {        
                "data": {
                    "account-number": "5WT0001",
                    "external-id": "A0000111111",
                    "opened-at": "2019-03-14T15:39:31.265+00:00",
                    "nickname": "Individual",
                    "account-type-name": "Individual",
                    "day-trader-status": False,
                    "is-closed": False,
                    "is-futures-approved": False,
                    "created-at": False,
                    "is-firm-error": False,
                    "is-firm-proprietary": False,
                    "is-test-drive": True,
                    "margin-or-cash": "Cash",
                    "is-foreign": False,
                    "funding-date": "2019-03-15"
                },
                "authority-level": "owner"
                }
    s = Mock()
    s.request.return_value = RequestResult(201, '', data=response)
    return s

@pytest.fixture
def account(session):
    acc = Account.get_account(session, "5WT0001")
    return acc

def test_get_all_accounts():
    response = {
                "data": {
                    "items": [
                        {
                            "account": {
                                "account-number": "5WT0001",
                                "external-id": "A0000196557",
                                "opened-at": "2019-03-14T15:39:31.265+00:00",
                                "nickname": "Individual",
                                "account-type-name": "Individual",
                                "day-trader-status": False,
                                "is-closed": False,
                                "is-futures-approved": False,
                                "created-at": False,
                                "is-firm-error": False,
                                "is-firm-proprietary": False,
                                "is-test-drive": True,
                                "margin-or-cash": "Cash",
                                "is-foreign": False,
                                "funding-date": "2019-03-15"
                            },
                            "authority-level": "owner"
                        },
                        {
                            "account": {
                                "account-number": "5WT0002",
                                "external-id": "A0000085347",
                                "opened-at": "2017-03-16T18:35:43.649+00:00",
                                "nickname": "Individual",
                                "account-type-name": "Individual",
                                "day-trader-status": False,
                                "is-closed": False,
                                "is-futures-approved": False,
                                "created-at": False,
                                "is-firm-error": False,
                                "is-firm-proprietary": False,
                                "is-test-drive": True,
                                "margin-or-cash": "Margin",
                                "is-foreign": False,
                                "funding-date": "2020-08-12"
                            },
                             "authority-level": "owner"
                        }
                        ]
                    }
                }
    session = Mock()
    session.request.return_value = RequestResult(200, '', data=response)  
    result = Account.get_accounts(session)
    assert all(isinstance(item, Account) for item in result)

def test_get_accounts_bad_request():
    session = Mock()
    session.request.side_effect = AdapterException()
    with pytest.raises(AdapterException):
        result = Account.get_accounts(session)
        assert result == []

def test_get_account_by_ID():
    response = {        
                "data": {
                    "account-number": "5WT0001",
                    "external-id": "A0000196557",
                    "opened-at": "2019-03-14T15:39:31.265+00:00",
                    "nickname": "Individual",
                    "account-type-name": "Individual",
                    "day-trader-status": False,
                    "is-closed": False,
                    "is-futures-approved": False,
                    "created-at": False,
                    "is-firm-error": False,
                    "is-firm-proprietary": False,
                    "is-test-drive": True,
                    "margin-or-cash": "Cash",
                    "is-foreign": False,
                    "funding-date": "2019-03-15"
                },
                "authority-level": "owner"
                }
    session = Mock()
    session.request.return_value = RequestResult(200, '', data=response)  
    result = Account.get_account(session, "5WT0001")
    assert isinstance(result, Account) and result.account_number == "5WT0001"

def test_get_account_by_id_bad_request():
    session = Mock()
    session.request.side_effect = AdapterException()
    with pytest.raises(AdapterException):
        result = Account.get_account(session, "5WT0001")
        assert result == []

def test_get_account_by_id_bad_account_number():
    session = Mock()
    session.request.side_effect = AdapterException('404: Not Found')
    with pytest.raises(AdapterException, match='404: Not Found'):
        result = Account.get_account(session, "5WT0002")
        assert result == None
        
def test_get_trading_status(session, account):
    response = {
        "data": {
            "account-number": "5WT0001",
            "equities-margin-calculation-type": "Reg T",
            "fee-schedule-name": "default",
            "futures-margin-rate-multiplier": "0.0",
            "has-intraday-equities-margin": False,
            "id": 10441,
            "is-aggregated-at-clearing": False,
            "is-closed": False,
            "is-closing-only": False,
            "is-cryptocurrency-closing-only": False,
            "is-cryptocurrency-enabled": False,
            "is-frozen": False,
            "is-full-equity-margin-required": False,
            "is-futures-closing-only": False,
            "is-futures-intra-day-enabled": False,
            "is-futures-enabled": False,
            "is-in-day-trade-equity-maintenance-call": False,
            "is-in-margin-call": False,
            "is-pattern-day-trader": False,
            "is-portfolio-margin-enabled": False,
            "is-risk-reducing-only": False,
            "is-small-notional-futures-intra-day-enabled": False,
            "is-roll-the-day-forward-enabled": True,
            "are-far-otm-net-options-restricted": True,
            "options-level": "No Restrictions",
            "short-calls-enabled": False,
            "small-notional-futures-margin-rate-multiplier": "0.0",
            "is-equity-offering-enabled": False,
            "is-equity-offering-closing-only": False,
            "enhanced-fraud-safeguards-enabled-at": "2023-05-11T11:12:06.323+00:00",
            "updated-at": "2023-05-11T11:12:06.323+00:00"
        },
        "context": "/accounts/5WT0001/trading-status"
    }
    session.request.return_value = RequestResult(200, '', data=response) 
    result = account.get_trading_status(session)
    assert isinstance(result, TradingStatus) and result.account_number == "5WT0001"

def test_get_trading_status_bad_request(session, account):
    session.request.side_effect = AdapterException()
    with pytest.raises(AdapterException):
        result = account.get_trading_status(session)
        assert result == None

def test_get_balances(session, account):
    response = {
    "data": {
        "account-number": "5WT0001",
        "cash-balance": "1000.0",
        "long-equity-value": "0.0",
        "short-equity-value": "0.0",
        "long-derivative-value": "0.0",
        "short-derivative-value": "0.0",
        "long-futures-value": "0.0",
        "short-futures-value": "0.0",
        "long-futures-derivative-value": "0.0",
        "short-futures-derivative-value": "0.0",
        "long-margineable-value": "0.0",
        "short-margineable-value": "0.0",
        "margin-equity": "1000.0",
        "equity-buying-power": "2000.0",
        "derivative-buying-power": "1000.0",
        "day-trading-buying-power": "0.0",
        "futures-margin-requirement": "0.0",
        "available-trading-funds": "0.0",
        "maintenance-requirement": "0.0",
        "maintenance-call-value": "0.0",
        "reg-t-call-value": "0.0",
        "day-trading-call-value": "0.0",
        "day-equity-call-value": "0.0",
        "net-liquidating-value": "1000.0",
        "cash-available-to-withdraw": "0.0",
        "day-trade-excess": "0.0",
        "pending-cash": "0.0",
        "pending-cash-effect": "None",
        "long-cryptocurrency-value": "0.0",
        "short-cryptocurrency-value": "0.0",
        "cryptocurrency-margin-requirement": "0.0",
        "unsettled-cryptocurrency-fiat-amount": "0.0",
        "unsettled-cryptocurrency-fiat-effect": "None",
        "closed-loop-available-balance": "0.0",
        "equity-offering-margin-requirement": "0.0",
        "long-bond-value": "0.0",
        "bond-margin-requirement": "0.0",
        "snapshot-date": "2023-05-23",
        "reg-t-margin-requirement": "0.0",
        "futures-overnight-margin-requirement": "0.0",
        "futures-intraday-margin-requirement": "0.0",
        "maintenance-excess": "1000.0",
        "pending-margin-interest": "0.0",
        "effective-cryptocurrency-buying-power": "0.0",
        "updated-at": "2023-05-11T11:12:08.392+00:00"
    },
    "context": "/accounts/5WT0001/balances"
}
    
    session.request.return_value = RequestResult(200, '', data=response) 
    result = account.get_balances(session)
    assert isinstance(result, AccountBalance) and result.account_number == "5WT0001"

def test_get_balances_bad_request(session, account):
    session.request.side_effect = AdapterException()
    with pytest.raises(AdapterException):
        result = account.get_balances(session)
        assert result == None

def test_get_balance_snapshots(session, account):
    response = {"data": {
            "items": [
                {
                    "account-number": "5WT0001",
                    "cash-balance": "1000.0",
                    "long-equity-value": "0.0",
                    "short-equity-value": "0.0",
                    "long-derivative-value": "0.0",
                    "short-derivative-value": "0.0",
                    "long-futures-value": "0.0",
                    "short-futures-value": "0.0",
                    "long-futures-derivative-value": "0.0",
                    "short-futures-derivative-value": "0.0",
                    "long-margineable-value": "0.0",
                    "short-margineable-value": "0.0",
                    "margin-equity": "1000.0",
                    "equity-buying-power": "2000.0",
                    "derivative-buying-power": "1000.0",
                    "day-trading-buying-power": "0.0",
                    "futures-margin-requirement": "0.0",
                    "available-trading-funds": "0.0",
                    "maintenance-requirement": "0.0",
                    "maintenance-call-value": "0.0",
                    "reg-t-call-value": "0.0",
                    "day-trading-call-value": "0.0",
                    "day-equity-call-value": "0.0",
                    "net-liquidating-value": "1000.0",
                    "cash-available-to-withdraw": "0.0",
                    "day-trade-excess": "0.0",
                    "pending-cash": "0.0",
                    "pending-cash-effect": "None",
                    "long-cryptocurrency-value": "0.0",
                    "short-cryptocurrency-value": "0.0",
                    "cryptocurrency-margin-requirement": "0.0",
                    "unsettled-cryptocurrency-fiat-amount": "0.0",
                    "unsettled-cryptocurrency-fiat-effect": "None",
                    "closed-loop-available-balance": "0.0",
                    "equity-offering-margin-requirement": "0.0",
                    "long-bond-value": "0.0",
                    "bond-margin-requirement": "0.0",
                    "snapshot-date": "2023-05-23",
                    "reg-t-margin-requirement": "0.0",
                    "futures-overnight-margin-requirement": "0.0",
                    "futures-intraday-margin-requirement": "0.0",
                    "maintenance-excess": "1000.0",
                    "pending-margin-interest": "0.0",
                    "effective-cryptocurrency-buying-power": "0.0",
                    "updated-at": "2023-05-11T11:12:08.392+00:00"
                }
            ]
        },
        "context": "/accounts/5WT0001/balance-snapshots"
    }

    session.request.return_value = RequestResult(200, '', data=response) 
    result = account.get_balance_snapshots(session)
    assert all(isinstance(item, AccountBalanceSnapshot) for item in result)

def test_get_balance_snapshots_bad_request(session, account):
    session.request.side_effect = AdapterException()
    with pytest.raises(AdapterException):
        result = account.get_balance_snapshots(session)
        assert result == None

def test_get_positions(session, account):
    response = {"data": {
            "items": [
                {
                    "account-number": "5WT0001",
                    "symbol": "UVIX",
                    "instrument-type": "Equity",
                    "underlying-symbol": "UVIX",
                    "quantity": 5,
                    "quantity-direction": "Long",
                    "close-price": "9.61",
                    "average-open-price": "43.75",
                    "average-yearly-market-close-price": "29.1",
                    "average-daily-market-close-price": "9.61",
                    "multiplier": 1,
                    "cost-effect": "Credit",
                    "is-suppressed": False,
                    "is-frozen": False,
                    "restricted-quantity": 0,
                    "realized-day-gain": "0.0",
                    "realized-day-gain-effect": "None",
                    "realized-day-gain-date": "2023-01-25",
                    "realized-today": "0.0",
                    "realized-today-effect": "None",
                    "realized-today-date": "2023-01-25",
                    "created-at": "2022-11-04T14:34:47.701+00:00",
                    "updated-at": "2023-01-25T11:57:48.019+00:00"
                }
            ]
        },
        "context": "/accounts/5WT0001/positions"
    }

    session.request.return_value = RequestResult(200, '', data=response) 
    result = account.get_positions(session)
    assert all(isinstance(item, Position) for item in result)

def test_get_positions_bad_request(session, account):
    session.request.side_effect = AdapterException()
    with pytest.raises(AdapterException):
        result = account.get_positions(session)
        assert result == None

def test_get_transactions(session, account):
    response = {"data": {
        "items": [
            {
                "id": 222222222,
                "account-number": "5WT0001",
                "symbol": "UVIX",
                "instrument-type": "Equity",
                "underlying-symbol": "UVIX",
                "transaction-type": "Receive Deliver",
                "transaction-sub-type": "Reverse Split",
                "description": "Reverse split: Open 5.0 UVIX",
                "action": "Buy to Open",
                "quantity": "5.0",
                "executed-at": "2023-01-25T11:57:46.893+00:00",
                "transaction-date": "2023-01-25",
                "value": "218.75",
                "value-effect": "Debit",
                "net-value": "218.75",
                "net-value-effect": "Debit",
                "is-estimated-fee": True
            },
            ]
        },
        "context": "/accounts/5WT0001/transactions",
        "pagination": {
            "per-page": 100,
            "page-offset": 0,
            "item-offset": 0,
            "total-items": 328,
            "total-pages": 1,
            "current-item-count": 100,
            "previous-link": None,
            "next-link": None,
            "paging-link-template": None
        }
    }

    session.request.return_value = RequestResult(200, '', data=response) 
    result = account.get_transactions(session)
    assert all(isinstance(item, Transaction) for item in result)

def test_get_transactions_bad_request(session, account):
    session.request.side_effect = AdapterException()
    with pytest.raises(AdapterException):
        result = account.get_transactions(session)
        assert result == None

def test_get_transaction(session, account):
    response = {"data": {
                "id": 222222222,
                "account-number": "5WT0001",
                "symbol": "UVIX",
                "instrument-type": "Equity",
                "underlying-symbol": "UVIX",
                "transaction-type": "Receive Deliver",
                "transaction-sub-type": "Reverse Split",
                "description": "Reverse split: Open 5.0 UVIX",
                "action": "Buy to Open",
                "quantity": "5.0",
                "executed-at": "2023-01-25T11:57:46.893+00:00",
                "transaction-date": "2023-01-25",
                "value": "218.75",
                "value-effect": "Debit",
                "net-value": "218.75",
                "net-value-effect": "Debit",
                "is-estimated-fee": True
            },
        "context": "/accounts/5WT0001/transactions",
    }
     
    session.request.return_value = RequestResult(200, '', data=response) 
    result = account.get_transaction(session, 222222222)
    assert isinstance(result, Transaction)

def test_get_transaction_by_id_bad_request(session, account):
    session.request.side_effect = AdapterException()
    with pytest.raises(AdapterException):
        result = account.get_transaction(session, 222222222)
        assert result == None

def test_get_transaction_by_id_bad_id_parameter(session, account):
    session.request.side_effect = AdapterException('404: Not Found')
    with pytest.raises(AdapterException, match='404: Not Found'):
        result = account.get_transaction(session, 222222223)
        assert result == None

def test_get_totalfees(session, account):
    response = {
        "data": {
            "total-fees": "0.0",
            "total-fees-effect": "None"
        },
        "context": "/accounts/5WT0001/transactions/total-fees"
    }
    session.request.return_value = RequestResult(200, '', data=response) 
    result = account.get_transaction(session)
    assert isinstance(result, TotalFees)

def test_get_net_liquidating_value_history(session, account):
    response = {"data": {
                "items": [
                {
                    "open": "81.657997131",
                    "high": "81.657997131",
                    "low": "81.657997131",
                    "close": "81.657997131",
                    "pending-cash-open": "0.0",
                    "pending-cash-high": "0.0",
                    "pending-cash-low": "0.0",
                    "pending-cash-close": "0.0",
                    "total-open": "81.657997131",
                    "total-high": "81.657997131",
                    "total-low": "81.657997131",
                    "total-close": "81.657997131",
                    "time": "2023-05-23 13:30:00+00"
                }
            ]
        }
    }
 
    session.request.return_value = RequestResult(200, '', data=response) 
    result = account.get_net_liquidating_value_history(session, time_back='1y')
    assert all(isinstance(item, NetLiquidation) for item in result)

def test_get_net_liquidating_value_histor_bad_request(session, account):
    session.request.side_effect = AdapterException()
    with pytest.raises(AdapterException):
        result = account.get_net_liquidating_value_history(session, time_back='1y')
        assert result == None

def test_get_effective_margin_requirements(session, account):
    response = {
                "data": {
                    "underlying-symbol": "UVIX",
                    "long-equity-initial": "0.75",
                    "short-equity-initial": "0.75",
                    "long-equity-maintenance": "0.75",
                    "short-equity-maintenance": "0.75",
                    "naked-option-standard": "0.75",
                    "naked-option-minimum": "0.35",
                    "naked-option-floor": "250.0"
                },
                "context": "/accounts/5WT0001/margin-requirements/UVIX/effective"
                }
 
    session.request.return_value = RequestResult(200, '', data=response) 
    result = account.get_effective_margin_requirements(session, 'UVIX')
    assert isinstance(result, MarginRequirement)


def test_get_effective_margin_requirements_bad_request(session, account):
    session.request.side_effect = AdapterException()
    with pytest.raises(AdapterException):
        result = account.get_effective_margin_requirements(session, 'UVIX')
        assert result == None

def test_get_position_limit(session, account):
    response = {
                "data": {
                    "account-number": "5WT0001",
                    "equity-order-size": 5000,
                    "equity-option-order-size": 1000,
                    "future-order-size": 250,
                    "future-option-order-size": 250,
                    "underlying-opening-order-limit": 50,
                    "equity-position-size": 50000,
                    "equity-option-position-size": 2000,
                    "future-position-size": 500,
                    "future-option-position-size": 500
                },
                "context": "/accounts/5WT0001/position-limit"
            }
 
    session.request.return_value = RequestResult(200, '', data=response) 
    result = account.get_position_limit(session)
    assert isinstance(result, PositionLimit)


def test_get_position_limit_bad_request(session, account):
    session.request.side_effect = AdapterException()
    with pytest.raises(AdapterException):
        result = account.get_position_limit(session)
        assert result == None


def test_get_margin_requirements(session, account):
    response = {
            "data": {
                "account-number": "5WT0001",
                "description": "Total",
                "margin-calculation-type": "Reg T",
                "option-level": "No Restrictions",
                "margin-requirement": "49.8",
                "margin-requirement-effect": "Debit",
                "initial-requirement": "49.8",
                "initial-requirement-effect": "Debit",
                "maintenance-requirement": "49.8",
                "maintenance-requirement-effect": "Debit",
                "margin-equity": "81.908",
                "margin-equity-effect": "Credit",
                "option-buying-power": "32.108",
                "option-buying-power-effect": "Credit",
                "reg-t-margin-requirement": "49.8",
                "reg-t-margin-requirement-effect": "Debit",
                "reg-t-option-buying-power": "32.108",
                "reg-t-option-buying-power-effect": "Credit",
                "maintenance-excess": "32.108",
                "maintenance-excess-effect": "Credit",
                "groups": [
                    {
                        "description": "UVIX",
                        "code": "UVIX",
                        "underlying-symbol": "UVIX",
                        "underlying-type": "Equity",
                        "expected-price-range-up-percent": "0.85",
                        "expected-price-range-down-percent": "0.85",
                        "point-of-no-return-percent": "1.01",
                        "margin-calculation-type": "Reg T",
                        "margin-requirement": "49.8",
                        "margin-requirement-effect": "Debit",
                        "initial-requirement": "49.8",
                        "initial-requirement-effect": "Debit",
                        "maintenance-requirement": "49.8",
                        "maintenance-requirement-effect": "Debit",
                        "buying-power": "49.8",
                        "buying-power-effect": "Credit",
                        "groups": [
                            {
                                "description": "LONG_UNDERLYING",
                                "margin-requirement": "49.8",
                                "margin-requirement-effect": "Debit",
                                "initial-requirement": "49.8",
                                "initial-requirement-effect": "Debit",
                                "maintenance-requirement": "49.8",
                                "maintenance-requirement-effect": "Debit",
                                "includes-working-order": False,
                                "buying-power": "49.8",
                                "buying-power-effect": "Credit",
                                "position-entries": [
                                    {
                                        "instrument-symbol": "UVIX",
                                        "instrument-type": "Equity",
                                        "quantity": "5.0",
                                        "close-price": "9.6",
                                        "fixing-price": "NaN"
                                    }
                                ]
                            }
                        ],
                        "price-increase-percent": "1.0",
                        "price-decrease-percent": "-1.0"
                    }
                ],
                "last-state-timestamp": 1684919088526
            }
        }

    session.request.return_value = RequestResult(200, '', data=response) 
    result = account.get_margin_requirements(session)
    assert isinstance(result, MarginReport)

def test_get_live_orders(session, account):
    response = {
            "data": {
                "items": [
                    {
                        "id": 269602377,
                        "account-number": "5WT0001",
                        "time-in-force": "GTC",
                        "order-type": "Limit",
                        "size": 1,
                        "underlying-symbol": "SNAP",
                        "underlying-instrument-type": "Equity",
                        "price": "0.04",
                        "price-effect": "Debit",
                        "status": "Received",
                        "cancellable": True,
                        "editable": True,
                        "edited": False,
                        "ext-exchange-order-number": "15651130429001",
                        "ext-client-order-id": "4900000e3c1011ce49",
                        "ext-global-order-number": 3644,
                        "received-at": "2023-05-22T17:13:27.578+00:00",
                        "updated-at": 1684872370980,
                        "legs": [
                            {
                                "instrument-type": "Equity Option",
                                "symbol": "SNAP  230602P00010000",
                                "quantity": 1,
                                "remaining-quantity": 1,
                                "action": "Buy to Close",
                                "fills": []
                            }
                        ]
                    }
                ]
            },
            "context": "/accounts/5WT0001/orders/live"
        }
    
    session.request.return_value = RequestResult(200, '', data=response) 
    result = account.get_live_orders(session)
    assert all(isinstance(item, PlacedOrder) for item in result)


def test_get_order(session, account):
    response = {
    "data": {
                "id": 269101311,
                "account-number": "5WU99764",
                "time-in-force": "GTC",
                "order-type": "Limit",
                "size": 1,
                "underlying-symbol": "SNAP",
                "underlying-instrument-type": "Equity",
                "price": "0.04",
                "price-effect": "Debit",
                "status": "Received",
                "cancellable": True,
                "editable": True,
                "edited": False,
                "ext-exchange-order-number": "15651130429001",
                "ext-client-order-id": "4900000e3c1011ce49",
                "ext-global-order-number": 3644,
                "received-at": "2023-05-22T17:13:27.578+00:00",
                "updated-at": 1684872370980,
                "legs": [
                    {
                        "instrument-type": "Equity Option",
                        "symbol": "SNAP  230602P00010000",
                        "quantity": 1,
                        "remaining-quantity": 1,
                        "action": "Buy to Close",
                        "fills": []
                    }
                ]
            },
            "context": "/accounts/5WT0001/orders/live"
        }
    
    session.request.return_value = RequestResult(200, '', data=response) 
    result = account.get_order(session, '269101311')
    assert isinstance(result, PlacedOrder)


