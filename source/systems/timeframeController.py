
from api import api
from models import timeframe
from models import candle
from systems import deltaController
from systems import configController
from systems import movingAverageController
from systems import signalController
from utilities import utils

class TimeframeController:
    def __init__(self, ticker:str, tf: str):
        self.__averagesController = movingAverageController.MovingAverageController(tf)
        self.__deltaController: deltaController.DeltaController = deltaController.DeltaController()
        self.__signalController: signalController.SignalController = signalController.SignalController(self)
        self.__finishedCandles = []
        self.__timeframe = timeframe.Timeframe[tf]
        self.__ticker = ticker
        self.__initCandles()
        self.__initControllers()
    
    def __getCandlesAmount(self):
        amountForAverages = self.__averagesController.getCandlesAmountForInit()
        return amountForAverages

    def __initCandles(self):
        amountForInit = self.__getCandlesAmount()
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

    def __initControllers(self):
        for candle in self.__finishedCandles:
            self.__averagesController.process(candle)
            self.__deltaController.process(candle)
        self.__signalController.update(self.__finishedCandles[-1]) # to do move to websocket

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

    def getAveragesController(self):
        return self.__averagesController
    
    def getDeltaController(self):
        return self.__deltaController
    
    def getSignalController(self):
        return self.__signalController

    def getCurrentCandle(self):
        # to do tmp
        if len(self.__finishedCandles) > 0:
            return self.__finishedCandles[-1]
        return candle.Candle()
