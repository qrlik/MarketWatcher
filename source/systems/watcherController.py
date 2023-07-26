from api import api
from systems import configController
from systems import tickerController
from systems import settingsController
from systems import websocketController
from utilities import utils

__tickers:dict = {}

def __getTickersList():
    infoFutures = api.Future.getExchangeInfo()
    basesFutures = dict()
    exceptions = settingsController.getSetting('baseAssetsExceptions')
    ignores = settingsController.getSetting('baseAssetsIgnores')
    spotIgnore = settingsController.getSetting('spotSymbolsExceptions')
    for symbol in infoFutures.get('symbols', []):
        name = symbol.get('symbol', '')
        status = symbol.get('status', '')
        baseAsset = symbol.get('baseAsset', '')
        quoteAsset = symbol.get('quoteAsset', '')
        underlyingType = symbol.get('underlyingType', '')
        contractType = symbol.get('contractType', '')

        if status == 'TRADING' and underlyingType == 'COIN' and quoteAsset == 'USDT' and contractType == 'PERPETUAL':
            if baseAsset in ignores:
                continue
            baseAsset = baseAsset.replace('1000', '')
            if exceptions.get(baseAsset, None):
                baseAsset = exceptions.get(baseAsset)
            basesFutures.setdefault(baseAsset, name)

    info = api.Spot.getExchangeInfo()
    tickers = set()
    basesSpot = set()
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

        for base in basesFutures.keys():
            if baseAsset == base:
                tickers.add((name, basesFutures[base], pricePrecision))
                basesSpot.add(baseAsset)
                break

    diffs = set(basesFutures.keys()).symmetric_difference(basesSpot)
    for spot in spotIgnore:
        diffs.discard(spot)
    if len(diffs) > 0:
        utils.log('watcherController::getTickersList not spot symbols - ' + str(diffs))

    return tickers

def getTickers():
    return __tickers

def getTicker(ticker:str):
    return __tickers.get(ticker)

def start():
    global __tickers
    timeframes = configController.getTimeframes()
    tickers = __getTickersList() #[('BTCUSDT', 2)]
    socketList = [ticker[0] for ticker in tickers]
    websocketController.start(socketList, timeframes)

    for ticker in tickers:
        controller = tickerController.TickerController(ticker[0], ticker[1], ticker[2])
        __tickers.setdefault(ticker[0], controller)
        controller.init()

def loop():
    allProgress = len(__tickers)
    curProgress = 0
    for _, controller in __tickers.items():
        curProgress += controller.loop()
    return int(curProgress / allProgress * 100)
