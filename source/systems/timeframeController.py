
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
        startPoint = utils.getCurrentTime() - amountForAverages * self.__timeframe
        cacheName = utils.cacheFolder + 'tickers/' + self.__ticker + '/' + self.__timeframe.name
        candles = utils.loadPickleJson(cacheName)
        candles = [] if candles is None else candles
        if candles and len(candles) > 0:
            lastCache = candles[-1].openTime + self.__timeframe
            if startPoint < lastCache:
                startPoint = lastCache
            else:
                candles = []

        # to do check first candle vs startPoint without cache

        candles.extend(api.Spot.getFinishedCandelsByStart(self.__ticker, self.__timeframe, startPoint))
        candles = candles[-amountForAverages:]
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

    __averagesController: movingAverageController.MovingAverageController = None
    __timeframe: timeframe.Timeframe = None
    __ticker:str = ''
    __lastClosedCandle:candle.Candle = None
    __currentCandle:candle.Candle = None