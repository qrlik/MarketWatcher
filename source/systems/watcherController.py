from api import api
from systems import tickerController

__tickers:dict = {}
__loading = False

def getTickers():
    global __loading
    if __loading:
        return {}
    return __tickers

def getTicker(ticker:str):
    return __tickers.get(ticker)

def requestTickers():
    return api.getTickersList()

def loadTickets(tickers):
    global __tickers,__loading
    __loading = True
    for ticker, info in tickers:
        controller = tickerController.TickerController(ticker, info)
        __tickers.setdefault(ticker, controller)
        controller.init()
    __loading = False

def loop():
    global __loading
    if __loading:
        return
    for _, controller in __tickers.items():
        controller.loop()
