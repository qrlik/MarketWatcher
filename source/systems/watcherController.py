from api import api
from systems import tickerController

__tickers:dict = {}

def __getFuturesTickersList():
    info = api.Future.getExchangeInfo()
    tickers = []
    for symbol in info.get('symbols', []):
        if symbol.get('status', '') == 'TRADING' and symbol.get('quoteAsset', '') == 'USDT':
            name = symbol.get('symbol')
            pricePrecision = symbol.get('pricePrecision')
            if name:
                tickers.append((name, pricePrecision))
    return tickers

def getTickers():
    return __tickers

def getTicker(ticker:str):
    return __tickers.get(ticker)

def start():
    __tickers.setdefault('BTCUSDT', tickerController.TickerController('BTCUSDT', 2))
    __tickers.setdefault('ETHUSDT', tickerController.TickerController('ETHUSDT', 2))
    x = 5
    # for ticker in getFuturesTickersList():
    #     self.__tickers.setdefault(ticker, tickerController.TickerController('BTCUSDT'))

def update():
    for _, controller in __tickers.items():
        controller.update()
