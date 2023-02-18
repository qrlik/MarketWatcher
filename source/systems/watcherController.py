from api import api
from systems import tickerController

def getFuturesTickersList():
    info = api.Future.getExchangeInfo()
    tickers = []
    for symbol in info.get('symbols', []):
        if symbol.get('status', '') == 'TRADING' and symbol.get('quoteAsset', '') == 'USDT':
            name = symbol.get('symbol')
            if name:
                tickers.append(name)
    return tickers

class WatcherController:
    def __init__(self):
        self.__tickers = getFuturesTickersList()
        x = tickerController.TickerController('BTCUSDT')
    
    __tickers = []
 