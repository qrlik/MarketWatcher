from models import candle
from systems import loaderController
from systems import watcherController
from utilities import utils

__cache = utils.loadJsonFile(utils.cacheFolder + 'cache')
__cache = __cache if __cache is not None else {}

__candlesCacheFile = utils.cacheFolder + 'candles'
__candles:dict = utils.loadJsonMsgspecFile(__candlesCacheFile)
__candles = __candles if __candles is not None else {}

def save():
    utils.saveJsonFile(utils.cacheFolder + 'cache', __cache)

def __setField(key:str, value):
    __cache.setdefault(key, value)
    save()

def __getField(key:str):
    return __cache.get(key)

def getLastConfigFilename():
    return __getField('lastConfigFilename')

def setLastConfigFilename(filename:str):
    return __setField('lastConfigFilename', filename)

def getCandles(ticker, timeframe):
    data = __candles.get(ticker, {}).pop(timeframe, [])
    candles = [candle.fromJson(c, timeframe) for c in data]
    return candles

def saveCandles():
    if not loaderController.isDone():
        return
    __candles.clear()
    for ticker, tickerController in watcherController.getTickers().items():
        for tf, tfController in tickerController.getTimeframes().items():
            __candles.setdefault(ticker, {}).setdefault(tf.name, tfController.getCandlesController().getJsonData())
    utils.saveJsonMsgspecFile(__candlesCacheFile, __candles)
    __candles.clear()
