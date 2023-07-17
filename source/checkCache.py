import asyncio
import os

from api import api
from api import apiRequests
from models import candle
from models import timeframe
from utilities import utils

async def checkFile(ticker, tf):
    cachedData = utils.loadJsonMsgspecFile(utils.cacheFolder + 'tickers/' + ticker + '/' + tf)
    cachedCandles = [candle.createFromDict(c) for c in cachedData] # to do
    if len(cachedCandles) == 0:
        utils.logError('checkCache: empty cache ' + ticker + ' ' + tf)
    cachedCandles.pop()
    if len(cachedCandles) == 0:
        return

    timestamp = cachedCandles[0].openTime
    if not timestamp:
        utils.logError('checkCache: empty timestamp ' + ticker + ' ' + tf)

    requestId = api.Spot.getCandlesByTimestamp(ticker, timeframe.Timeframe[tf], len(cachedCandles), timestamp)
    serverData = None
    while serverData is None:
        serverData = apiRequests.requester.getResponse(requestId)

    if len(cachedCandles) != len(serverData):
        utils.logError('checkCache: wrong length ' + ticker + ' ' + tf)
    for i in range(len(cachedCandles)):
        cached = cachedCandles[i]
        server = serverData[i]
        if cached != server:
            utils.logError('checkCache: not equal ' + ticker + ' ' + tf)
    checkCandlesSequence(ticker, tf, cachedCandles)

#its ok
#LUNAUSDT 04:00 30-05-2022
#KEYUSDT 04:00 10-03-2023

def checkCandlesSequence(ticker, timeframe, candles):
    if len(candles) == 0:
        return
    lastOpen = candles[0].openTime
    errorStr = 'TimeframeController: ' + ticker + ' ' + timeframe
    if len(candles) > 1:
        for candle in candles[1:]:
            if lastOpen + candle.interval != candle.openTime:
                utils.logError(errorStr + ' wrong finish sequence ' + candle.time)
            lastOpen = candle.openTime

async def checkCacheFolder():
    if not os.path.exists(utils.cacheFolder):
        utils.logError('checkCache: no cache folder')
    if not os.path.exists('cache/tickers'):
        utils.logError('checkCache: no tickers folder')
        
    for folder in os.scandir('cache/tickers/'):
        if folder.is_dir():
            for file in os.listdir(folder.path):
                await checkFile(folder.name, file.split('.')[0])
        print(folder.name + ' finished')
    print('check finished')


if __name__ == "__main__":
    asyncio.run(checkCacheFolder())