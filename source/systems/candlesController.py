from api import api
from models import timeframe
from models import candle
from utilities import utils

class CandlesController:
    def __init__(self, ticker:str, tf: str, amountForInit):
        self.__finishedCandles = []
        self.__timeframe = timeframe.Timeframe[tf]
        self.__ticker = ticker
        self.__initCandles(amountForInit)
    
    def __initCandles(self, amountForInit):
        amountForRequest = amountForInit
        cacheName = utils.cacheFolder + 'tickers/' + self.__ticker + '/' + self.__timeframe.name
        candles = utils.loadPickleJson(cacheName)
        candles = [] if candles is None else candles
        if candles and len(candles) > 0:
            lastCache = candles[-1].openTime + self.__timeframe
            timeFromCache = utils.getCurrentTime() - lastCache
            finishedFromCache = int(timeFromCache / self.__timeframe)
            if finishedFromCache >= amountForInit:
                candles = []
            else:
                amountForRequest = finishedFromCache
            
        candles.extend(api.Spot.getFinishedCandles(self.__ticker, self.__timeframe, amountForRequest))
        candles = candles[-amountForInit:]
        self.__checkFinishedCandles(candles)
        utils.savePickleJson(cacheName, candles)
        self.__finishedCandles = candles

    def __checkFinishedCandles(self, candles):
        if not utils.isDebug() or len(candles) < 2:
            return
        lastOpen = candles[0].openTime
        errorStr = 'TimeframeController: ' + self.__ticker + ' ' + self.__timeframe.name
        for candle in candles[1:]:
            if lastOpen + self.__timeframe != candle.openTime:
                utils.logError(errorStr + ' wrong sequence')
            lastOpen = candle.openTime

        isWeek = self.__timeframe == timeframe.Timeframe.ONE_WEEK
        time = utils.getCurrentTime() if not isWeek else utils.getCurrentTime() - 4 * timeframe.Timeframe.ONE_DAY
        currentCandleOpen = int(time / self.__timeframe) * self.__timeframe
        currentCandleOpen = currentCandleOpen if not isWeek else currentCandleOpen + 4 * timeframe.Timeframe.ONE_DAY

        if currentCandleOpen != candles[-1].openTime + self.__timeframe:
            utils.logError(errorStr + ' wrong last finished candle')

    def getFinishedCandles(self):
        return self.__finishedCandles
    
    def getLastFinishedCandle(self):
        if len(self.__finishedCandles) > 0:
            return self.__finishedCandles[-1]
        return candle.Candle()

    #def getCurrentCandle(self):
        # to do tmp
        # # to do move to websocket?
        if len(self.__finishedCandles) > 0:
            return self.__finishedCandles[-1]
        return candle.Candle()
    
