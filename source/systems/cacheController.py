from enum import Enum
from models import candle
from systems import loaderController
from systems import watcherController
from utilities import workMode
from utilities import utils

__cache:dict = None
__candles:dict = None
__lastCandlesCheck = {}

def load():
    global __cache,__candles
    __cache = utils.loadJsonFile(workMode.getCacheFile())
    __cache = __cache if __cache is not None else {}

    __candles = utils.loadJsonFile(workMode.getCacheCandlesFile())
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
    if workMode.isCrypto():
        candles = [candle.fromJson(c, timeframe) for c in data]
    else:
        candles = [candle.fromSpotJson(c, timeframe) for c in data]
    return candles

def saveCandles():
    if not loaderController.isDone() or not loaderController.isValid():
        return
    __candles.clear()
    for ticker, tickerController in watcherController.getTickers().items():
        for tf, tfController in tickerController.getTimeframes().items():
            __candles.setdefault(ticker, {}).setdefault(tf.name, tfController.getCandlesController().getJsonData())
    utils.saveJsonFile(workMode.getCacheCandlesFile(), __candles)
    
def __getViewedDivergences():
    return __cache.setdefault("viewedDivergences", {})

def __getViewedChannels():
    return __cache.setdefault("viewedChannels", {})

def __getDatestamp(type):
    return __cache.setdefault(type.name, {})

def setChannelViewed(ticker:str, timeframe:str, channelKey):
    state = __getViewedChannels().setdefault(ticker, {}).setdefault(timeframe, {})
    state.setdefault(channelKey, True)
    state[channelKey] = True

def setDivergenceViewed(ticker:str, timeframe:str, time1:str, time2:str, value):
    state = __getViewedDivergences().setdefault(ticker, {}).setdefault(timeframe, {}).setdefault(time1, {})
    state.setdefault(time2, value)
    state[time2] = value

def updateViewedChannels(ticker:str, timeframe:str, channels):
    forRemove = []
    viewedChannels = __getViewedChannels().get(ticker, {}).get(timeframe, {})

    for viewedChannel, value in viewedChannels.items():
        found = False
        for channel in channels:
            if channel.getDictKey() == viewedChannel:
                found = True
                channel.viewed = value
                break
        if not found:
            forRemove.append(viewedChannel)
    
    for remove in forRemove:
        viewedChannels.pop(remove, None)
 
def updateViewedDivergences(ticker:str, timeframe:str, divers):
    forRemove1 = []
    times1 = __getViewedDivergences().get(ticker, {}).get(timeframe, {})

    for time1, times2 in times1.items():
        forRemove2 = []
        for time2, value in times2.items():
            found = False
            for divergence in divers:
                if divergence.firstCandle.time == time1 and divergence.secondCandle.time == time2:
                    found = True
                    divergence.viewed = value
                    break
            if not found:
                forRemove2.append(time2)
        for remove in forRemove2:
            times2.pop(remove, None)
        if len(times2) == 0:
            forRemove1.append(time1)
    
    for remove in forRemove1:
        times1.pop(remove, None)
 
def updateLastCandlesCheck(lastTime, timeframe, ticker):
    global __lastCandlesCheck
    lastTimestamps = __lastCandlesCheck.setdefault(timeframe.name, [])
    founded = False
    for time, tickers in lastTimestamps:
        if time == lastTime:
            founded = True
            tickers.append(ticker)
    if not founded:
        lastTimestamps.append((lastTime, [ticker]))

def saveLastCandlesCheck():
    global __lastCandlesCheck
    for timeframe, timestamps in __lastCandlesCheck.items():
        if len(timestamps) == 0:
            utils.log('Last open check - ' + timeframe + ' empty')
        elif len(timestamps) == 1:
            utils.log('Last open check - ' + timeframe + ' ' + timestamps[0][0])
        else:
            timestamps.sort(key = lambda tuple: len(tuple[1]),reverse=True)
            for _, tickers in timestamps[1:]:
                for ticker in tickers:
                    watcherController.getTicker(ticker).setInvalidLastCandle()
            utils.log('Last open check - ' + timeframe + ' ' + timestamps[0][0] + ', FAILED')
    utils.saveJsonFile(workMode.getCacheLastOpenCheckFile(), __lastCandlesCheck)

class DateStamp(Enum):
    VIEWED = 0,
    BORED = 1

def setDatestamp(ticker, type, timestamp):
    if timestamp:
        typeDict = __getDatestamp(type)
        typeDict.setdefault(ticker, timestamp)
        typeDict[ticker] = timestamp
    else:
        __getDatestamp(type).pop(ticker, None)

def getDatestamp(ticker, type):
    return __getDatestamp(type).setdefault(ticker, None)

def getBoredCount(ticker):
    dict = __cache.setdefault("boredAmount", {})
    amount = dict.setdefault(ticker, 0)
    return dict[ticker]

def setBoredCount(ticker, amount):
    dict = __cache.setdefault("boredAmount", {})
    dict.setdefault(ticker, amount)
    dict[ticker] = amount