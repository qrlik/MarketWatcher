
from api import api
from models import timeframe
from models import candle
from systems import configController
from systems import movingAverageController
from utilities import utils

class TimeframeController:
    def __init__(self, ticker:str, tf: str):
        self.__averagesController = movingAverageController.MovingAverageController(configController.getMovingAverages(tf))
        self.__timeframe = timeframe.Timeframe[tf]
        self.__ticker = ticker
        self.__initCandles()
    
    def __initCandles(self):
        amountForAverages = self.__averagesController.getCandlesAmountForInit()
        cacheName = utils.cacheFolder + 'tickers/' + self.__ticker + '/' + self.__timeframe.name
        candles = utils.loadPickleJson(cacheName)
        candles = [] if candles is None else candles
        if candles and len(candles) > 0:
            lastCache = candles[-1].openTime + self.__timeframe
            timeFromCache = utils.getCurrentTime() - lastCache
            finishedFromCache = int(timeFromCache / self.__timeframe)
            if finishedFromCache >= amountForAverages:
                candles = []
            else:
                amountForAverages = finishedFromCache
            
        candles.extend(api.Spot.getFinishedCandles(self.__ticker, self.__timeframe, amountForAverages))
        candles = candles[-amountForAverages:]
        self.__checkFinishedCandles(candles)
        utils.savePickleJson(cacheName, candles)

        if len(candles) == 0:
            return
        self.__currentCandle = candles[-1]
        candles.pop()
        if len(candles) == 0:
            return
        self.__lastClosedCandle = candles[-1]
        for candle in candles:
            self.__averagesController.process(candle)

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


    __averagesController: movingAverageController.MovingAverageController = None
    __timeframe: timeframe.Timeframe = None
    __ticker:str = ''
    __lastClosedCandle:candle.Candle = None
    __currentCandle:candle.Candle = None