import asyncio
import os

from api import api
from models import candle
from models import timeframe
from utilities import utils

async def checkFile(ticker, tf):
    cachedData = utils.loadJsonMsgspecFile(utils.cacheFolder + 'tickers/' + ticker + '/' + tf)
    cachedCandles = [candle.createFromDict(c) for c in cachedData]
    if len(cachedCandles) == 0:
        utils.logError('checkCache: empty cache ' + ticker + ' ' + tf)
    cachedCandles.pop()
    if len(cachedCandles) == 0:
        return

    timestamp = cachedCandles[0].openTime
    if not timestamp:
        utils.logError('checkCache: empty timestamp ' + ticker + ' ' + tf)

    #can raise exception
    serverData = await api.Spot.__getCandlesByTimestamp(ticker, timeframe.Timeframe[tf], len(cachedCandles), timestamp)
    if len(cachedCandles) != len(serverData):
        utils.logError('checkCache: wrong length ' + ticker + ' ' + tf)
    for i in range(len(cachedCandles)):
        cached = cachedCandles[i]
        server = serverData[i]
        if cached != server:
            utils.logError('checkCache: not equal ' + ticker + ' ' + tf)

async def checkCacheFolder():
    if not os.path.exists(utils.cacheFolder):
        utils.logError('checkCache: no cache folder')
    if not os.path.exists('cache/tickers'):
        utils.logError('checkCache: no tickers folder')
        
    for folder in os.scandir('cache/tickers/'):
        if folder.is_dir():
            for file in os.listdir(folder.path):
                await checkFile(folder.name, file.split('.')[0])
    print('check finished')


if __name__ == "__main__":
    asyncio.run(checkCacheFolder())