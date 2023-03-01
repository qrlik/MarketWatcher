from api import api
from systems import tickerController

__tickers:dict = {}

def __getFuturesTickersList():
    info = api.Future.getExchangeInfo()
    tickers = []
    for symbol in info.get('symbols', []):
        if symbol.get('status', '') == 'TRADING' and symbol.get('quoteAsset', '') == 'USDT':
            name = symbol.get('symbol')
            if name:
                tickers.append(name)
    return tickers

def getTickers():
    return __tickers

def start():
    __tickers.setdefault('BTCUSDT', tickerController.TickerController('BTCUSDT'))
    # for ticker in getFuturesTickersList():
    #     self.__tickers.setdefault(ticker, tickerController.TickerController('BTCUSDT'))
