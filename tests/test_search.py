from unittest.mock import patch, Mock
from ttapi.account import Account
from ttapi.search import symbol_search
from ttapi.models import SymbolData, RequestResult


def test_search():
    response = {"data": {
        "items": [
            {
                "symbol": "VIS",
                "description": "Vanguard Industrials ETF"
            },
            {
                "symbol": "VIST",
                "description": "Vista Oil & Gas, S.A.B. de C.V. American Depositary Shares, each representing one series A share, with no par value"
            }
        ]
    }}

    session = Mock()
    session.request.return_value = RequestResult(200, '', data=response) 
    result = symbol_search(session, 'VI')
    assert all(isinstance(item, SymbolData) for item in result)