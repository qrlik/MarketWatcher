from models import candle
from systems import loaderController
from systems import watcherController
from utilities import workMode
from utilities import utils

__cache:dict = None
__candles:dict = None

def load():
    global __cache,__candles
    __cache = utils.loadJsonFile(workMode.getCacheFile())
    __cache = __cache if __cache is not None else {}

    __candles = utils.loadJsonMsgspecFile(workMode.getCacheCandlesFile())
    __candles = __candles if __candles is not None else {}

def save():
    utils.saveJsonFile(workMode.getCacheFile(), __cache)

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
    utils.saveJsonMsgspecFile(workMode.getCacheCandlesFile(), __candles)
    __candles.clear()
