from utilities import utils

__cache = utils.loadJsonFile(utils.cacheFolder + 'cache')
__cache = __cache if __cache is not None else {}

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

def __getViewedDivergences():
    return __cache.setdefault("viewedDivergences", {})

def setDivergenceViewed(ticker:str, timeframe:str, time1:str, time2:str, value):
    state = __getViewedDivergences().setdefault(ticker, {}).setdefault(timeframe, {}).setdefault(time1, {})
    state.setdefault(time2, value)
    state[time2] = value
    save()

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
