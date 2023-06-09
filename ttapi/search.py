from ttapi.models import SymbolData
from ttapi.session import Session

def symbol_search(session: Session, symbol: str) -> list[SymbolData]:
    """
    Performs a symbol search and returns a list of symbols that
    are similar to the given search phrase.

    :param session: active user session to use
    :param symbol: search phrase

    :return: a list of symbols and descriptions that match the search phrase
    """
    symbol = symbol.replace('/', '%2F')
    response = session.request('GET', f'/symbols/search/{symbol}')
    return [SymbolData(**entry) for entry in response.data['data']['items']]