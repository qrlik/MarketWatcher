from api import api
from systems import configController
from systems import tickerController
from systems import websocketController
from utilities import utils

__tickers:dict = {}

def __getTickersList():
    infoFutures = api.Future.getExchangeInfo()
    tickersFutures = []
    for symbol in infoFutures.get('symbols', []):
        name = symbol.get('symbol', None)
        status = symbol.get('status', '')
        underlyingType = symbol.get('underlyingType', '')

        if status == 'TRADING' and underlyingType == 'COIN':
            tickersFutures.append(name)

    info = api.Spot.getExchangeInfo()
    tickers = []
    for symbol in info.get('symbols', []):
        name = symbol.get('symbol', None)
        baseAsset = symbol.get('baseAsset', '')
        quoteAsset = symbol.get('quoteAsset', '')
        status = symbol.get('status', '')
        pricePrecision = 0
        pricePrecisionFloat = 1.0

        if status != 'TRADING' or quoteAsset != 'USDT':
            continue

        for filter in symbol.get('filters', {}):
            if filter.get('filterType', '') == 'PRICE_FILTER':
                pricePrecisionFloat = float(filter.get('tickSize', 1.0))
                break

        while pricePrecisionFloat < 1.0:
            pricePrecision += 1
            pricePrecisionFloat *= 10

        for ticker in tickersFutures:
            if baseAsset in ticker and quoteAsset in ticker:
                tickers.append((name, pricePrecision))
                break

    return tickers

def getTickers():
    return __tickers

def getTicker(ticker:str):
    return __tickers.get(ticker)

def start():
    global __tickers
    timeframes = configController.getTimeframes() #[timeframe.Timeframe.ONE_MIN]
    tickers = __getTickersList() #[('BTCUSDT', 2), ('ETHUSDT', 1)]#
    socketList = [ticker[0] for ticker in tickers]
    websocketController.start(socketList, timeframes[0])

    for ticker in tickers:
        controller = tickerController.TickerController(ticker[0], ticker[1])
        __tickers.setdefault(ticker[0], controller)
        controller.init()

def update():
    result = 0
    for _, controller in __tickers.items():
        result += controller.update()

    print(str(result) + '/' + str(len(__tickers)))
